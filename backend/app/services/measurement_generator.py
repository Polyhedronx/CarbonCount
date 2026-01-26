import random
import math
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..core.database import SessionLocal
from ..models import CarbonZone, ZoneMeasurement, ZoneStatus

logger = logging.getLogger(__name__)

# ==================== 辅助函数 ====================

def get_seasonal_factor(date: datetime) -> float:
    """
    计算季节性因子（基于月份）
    6月（夏季）为峰值1.0，12月（冬季）为谷值0.5
    """
    month = date.month
    # 使用正弦函数：6月为峰值，12月为谷值
    # 调整相位使6月达到峰值
    seasonal = 0.5 + 0.4 * math.sin((month - 3) * math.pi / 6)
    return max(0.4, min(1.0, seasonal))


def infer_ecosystem_type(zone: CarbonZone) -> str:
    """
    根据区域名称推断生态系统类型
    """
    name_lower = zone.name.lower()
    if any(keyword in name_lower for keyword in ['森林', '林', 'forest', 'wood']):
        return 'forest'
    elif any(keyword in name_lower for keyword in ['草地', '草原', 'grassland', 'meadow']):
        return 'grassland'
    elif any(keyword in name_lower for keyword in ['湿地', 'wetland', 'marsh', 'swamp']):
        return 'wetland'
    elif any(keyword in name_lower for keyword in ['农田', 'farm', 'crop', 'field']):
        return 'farmland'
    else:
        return 'mixed'  # 默认混合类型


def get_ecosystem_params(ecosystem_type: str) -> Tuple[float, float, float]:
    """
    返回生态系统类型的基础参数：(基础NDVI最小值, 基础NDVI最大值, 碳吸收系数)
    """
    params = {
        'forest': (0.55, 0.85, 0.0008),      # 森林：高NDVI，高碳吸收
        'grassland': (0.40, 0.70, 0.0004),  # 草地：中等NDVI，中等碳吸收
        'wetland': (0.50, 0.80, 0.0006),    # 湿地：较高NDVI，较高碳吸收
        'farmland': (0.30, 0.75, 0.0005),  # 农田：变化大，中等碳吸收
        'mixed': (0.45, 0.75, 0.0005)      # 混合：中等参数
    }
    return params.get(ecosystem_type, params['mixed'])


def get_latitude_from_coordinates(zone: CarbonZone) -> Optional[float]:
    """
    从坐标中提取平均纬度
    """
    try:
        coords = zone.coordinates_list
        if coords and len(coords) > 0:
            latitudes = []
            for coord in coords:
                if isinstance(coord, dict):
                    lat = coord.get('lat')
                elif isinstance(coord, (list, tuple)) and len(coord) >= 2:
                    lat = coord[0]  # 假设是 [lat, lng] 格式
                else:
                    lat = None
                if lat is not None:
                    latitudes.append(float(lat))
            
            if latitudes:
                return sum(latitudes) / len(latitudes)
    except Exception as e:
        logger.debug(f"Error extracting latitude from coordinates: {e}")
    return None


def get_base_ndvi_range(zone: CarbonZone, ecosystem_type: str) -> Tuple[float, float]:
    """
    根据生态系统类型和地理位置确定基础NDVI范围
    """
    min_ndvi, max_ndvi, _ = get_ecosystem_params(ecosystem_type)
    
    # 根据纬度调整（南方高，北方低）
    latitude = get_latitude_from_coordinates(zone)
    if latitude:
        if latitude < 25:  # 南方
            adjustment = 0.05
        elif latitude < 35:  # 中部
            adjustment = 0.0
        else:  # 北方
            adjustment = -0.05
        min_ndvi += adjustment
        max_ndvi += adjustment
    
    return (max(0.2, min_ndvi), min(0.95, max_ndvi))


def get_area_efficiency_factor(area_hectares: float) -> float:
    """
    根据面积计算效率因子（考虑规模效应）
    - 小面积（<1公顷）：效率因子 > 1.0（1.1-1.2）
    - 中等面积（1-100公顷）：效率因子 ≈ 1.0
    - 大面积（>100公顷）：效率因子 < 1.0（0.9-0.95）
    """
    if area_hectares < 1:
        return 1.0 + 0.2 * (1 - area_hectares)  # 1.0-1.2
    elif area_hectares < 100:
        return 1.0
    else:
        return 1.0 - 0.05 * min(1.0, (area_hectares - 100) / 900)  # 0.95-1.0


def get_seasonal_carbon_factor(date: datetime) -> float:
    """
    计算季节性对碳吸收量的直接影响因子
    6月峰值1.2，12月谷值0.7
    """
    month = date.month
    # 使用正弦函数，6月为峰值，12月为谷值
    seasonal = 0.95 + 0.25 * math.sin((month - 3) * math.pi / 6)
    return max(0.7, min(1.2, seasonal))


def get_latitude_carbon_factor(latitude: Optional[float]) -> float:
    """
    根据纬度计算碳吸收效率因子
    - 南方（<25°N）：生长期长，效率高（+5-10%）
    - 中部（25-35°N）：标准效率
    - 北方（>35°N）：生长期短，效率低（-5-10%）
    """
    if latitude is None:
        return 1.0
    
    if latitude < 25:  # 南方
        return 1.05 + 0.05 * (25 - latitude) / 25  # 1.05-1.10
    elif latitude < 35:  # 中部
        return 1.0
    else:  # 北方
        return 1.0 - 0.05 * min(1.0, (latitude - 35) / 20)  # 0.95-1.0


def apply_weather_carbon_effect(
    base_carbon: float, 
    date: datetime,
    ndvi: float
) -> float:
    """
    应用天气事件对碳吸收量的直接影响
    与NDVI的天气影响同步（使用相同的随机种子或状态）
    """
    # 使用日期和NDVI的组合作为随机种子，确保与NDVI的天气影响一致
    # 保存当前随机状态
    random_state = random.getstate()
    random.seed(int(date.timestamp()) + int(ndvi * 10000))
    weather_event = random.choices(
        ['normal', 'drought', 'rainy'],
        weights=[0.90, 0.05, 0.05]
    )[0]
    # 恢复随机状态
    random.setstate(random_state)
    
    if weather_event == 'drought':
        return base_carbon * 0.82  # 下降18%
    elif weather_event == 'rainy':
        return base_carbon * 1.12  # 上升12%
    return base_carbon


def get_ecosystem_maturity_factor(zone: CarbonZone) -> float:
    """
    根据区域创建时间计算成熟度因子
    - 新建（<1年）：效率因子0.8-0.9
    - 成长中（1-5年）：效率因子0.9-1.0
    - 成熟（>5年）：效率因子1.0-1.1
    """
    # 防御性检查：如果 created_at 不存在，使用默认值1.0（假设是成熟系统）
    if not hasattr(zone, 'created_at') or zone.created_at is None:
        logger.warning(f"Zone {zone.id} has no created_at, using default maturity factor 1.0")
        return 1.0
    
    try:
        age_years = (datetime.now() - zone.created_at).days / 365.0
        
        if age_years < 1:
            return 0.8 + 0.1 * age_years  # 0.8-0.9
        elif age_years < 5:
            return 0.9 + 0.1 * (age_years - 1) / 4  # 0.9-1.0
        else:
            return 1.0 + 0.1 * min(1.0, (age_years - 5) / 10)  # 1.0-1.1
    except Exception as e:
        logger.warning(f"Error calculating maturity factor for zone {zone.id}: {e}, using default 1.0")
        return 1.0


def calculate_base_carbon_rate(ndvi: float, ecosystem_type: str) -> float:
    """
    计算基础碳吸收速率（基于NDVI和生态系统类型，不考虑其他因素）
    """
    _, _, carbon_coeff = get_ecosystem_params(ecosystem_type)
    
    # NDVI与碳吸收量的非线性关系
    if ndvi < 0.3:
        # 极低植被覆盖，碳吸收量接近0
        base_rate = 0.00001
    elif ndvi < 0.6:
        # 中等植被，线性增长
        base_rate = carbon_coeff * 0.5 * ((ndvi - 0.3) / 0.3)
    else:
        # 高植被，指数增长
        base_rate = carbon_coeff * (0.5 + 0.5 * ((ndvi - 0.6) / 0.4) ** 1.3)
    
    return base_rate


def calculate_carbon_absorption(
    ndvi: float, 
    area: float, 
    ecosystem_type: str,
    timestamp: datetime,
    zone: CarbonZone
) -> float:
    """
    优化后的碳吸收量计算（考虑多种因素）
    基于NDVI、面积、生态系统类型、时间、地理位置、成熟度等因素
    """
    # 1. 基础速率（基于NDVI和生态系统类型）
    base_rate = calculate_base_carbon_rate(ndvi, ecosystem_type)
    
    # 2. 面积调整（考虑规模效应）
    area_hectares = area / 10000
    area_factor = get_area_efficiency_factor(area_hectares)
    
    # 3. 季节性因子
    seasonal_factor = get_seasonal_carbon_factor(timestamp)
    
    # 4. 地理位置因子
    latitude = get_latitude_from_coordinates(zone)
    latitude_factor = get_latitude_carbon_factor(latitude)
    
    # 5. 生态系统成熟度因子
    maturity_factor = get_ecosystem_maturity_factor(zone)
    
    # 6. 计算总碳吸收量
    carbon_absorption = (
        base_rate * 
        area_hectares * 
        area_factor * 
        seasonal_factor * 
        latitude_factor * 
        maturity_factor
    )
    
    # 7. 应用天气事件影响
    carbon_absorption = apply_weather_carbon_effect(
        carbon_absorption, timestamp, ndvi
    )
    
    # 8. 添加小幅随机波动（±3%，因为已经有很多因子了）
    carbon_absorption *= random.uniform(0.97, 1.03)
    
    return max(0.00001, round(carbon_absorption, 6))


def apply_weather_effect(base_ndvi: float, date: datetime) -> float:
    """
    模拟天气事件对NDVI的影响
    """
    # 5%概率出现干旱，5%概率出现降雨
    weather_event = random.choices(
        ['normal', 'drought', 'rainy'],
        weights=[0.90, 0.05, 0.05]
    )[0]
    
    if weather_event == 'drought':
        return max(0.2, base_ndvi * 0.88)  # 下降12%
    elif weather_event == 'rainy':
        return min(0.95, base_ndvi * 1.08)  # 上升8%
    return base_ndvi


# ==================== 核心生成函数 ====================

def generate_measurement_at_time(
    zone: CarbonZone,
    timestamp: datetime,
    previous_ndvi: Optional[float] = None,
    ecosystem_type: Optional[str] = None
) -> Tuple[float, float]:
    """
    为指定区域在指定时间生成测量数据
    
    返回: (ndvi, carbon_absorption)
    """
    if ecosystem_type is None:
        ecosystem_type = infer_ecosystem_type(zone)
    
    # 获取基础NDVI范围
    min_ndvi, max_ndvi = get_base_ndvi_range(zone, ecosystem_type)
    
    # 计算季节性因子
    seasonal_factor = get_seasonal_factor(timestamp)
    
    # 计算基础NDVI（考虑季节性）
    base_ndvi_range = (
        min_ndvi + (max_ndvi - min_ndvi) * (seasonal_factor - 0.4) / 0.6
    )
    
    # 如果有历史数据，基于历史数据生成连续变化
    if previous_ndvi is not None:
        # 计算趋势（季节性变化）
        target_ndvi = base_ndvi_range + (max_ndvi - min_ndvi) * 0.2 * random.uniform(-1, 1)
        # 平滑过渡（每次变化不超过5%）
        change_limit = abs(previous_ndvi) * 0.05
        change = random.uniform(-change_limit, change_limit)
        # 向目标值靠近
        direction = 1 if target_ndvi > previous_ndvi else -1
        change = direction * min(abs(change), abs(target_ndvi - previous_ndvi) * 0.3)
        ndvi = previous_ndvi + change
    else:
        # 初始NDVI
        ndvi = base_ndvi_range + random.uniform(-0.1, 0.1) * (max_ndvi - min_ndvi)
    
    # 应用天气影响
    ndvi = apply_weather_effect(ndvi, timestamp)
    
    # 确保在合理范围内
    ndvi = max(0.2, min(0.95, ndvi))
    ndvi = round(ndvi, 4)
    
    # 计算碳吸收量（使用优化后的函数，传递所有必要参数）
    carbon_absorption = calculate_carbon_absorption(
        ndvi, zone.area, ecosystem_type, timestamp, zone
    )
    
    return (ndvi, carbon_absorption)


def generate_historical_measurements_for_zone(
    db: Session,
    zone: CarbonZone,
    days: int = 180,
    hours_interval: int = 12,
    force_regenerate: bool = False
) -> int:
    """
    为指定区域生成历史测量数据
    
    Args:
        db: 数据库会话
        zone: 监测区对象
        days: 生成多少天的历史数据（默认180天，即半年）
        hours_interval: 测量间隔（小时，默认12小时）
        force_regenerate: 是否强制重新生成（删除旧数据）
    
    Returns:
        生成的数据条数
    """
    # 检查是否已有数据
    existing_count = db.query(func.count(ZoneMeasurement.id)).filter(
        ZoneMeasurement.zone_id == zone.id
    ).scalar()
    
    if existing_count > 0 and not force_regenerate:
        logger.info(f"Zone {zone.id} already has {existing_count} measurements, skipping")
        return 0
    
    # 如果强制重新生成，删除旧数据
    if force_regenerate and existing_count > 0:
        db.query(ZoneMeasurement).filter(
            ZoneMeasurement.zone_id == zone.id
        ).delete()
        db.commit()
        logger.info(f"Deleted {existing_count} existing measurements for zone {zone.id}")
    
    # 计算时间范围
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    # 生成时间点列表（每12小时一次）
    time_points = []
    current_time = start_time
    # 对齐到整点（00:00或12:00）
    if current_time.hour < 12:
        current_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        current_time = current_time.replace(hour=12, minute=0, second=0, microsecond=0)
    
    while current_time <= end_time:
        time_points.append(current_time)
        current_time += timedelta(hours=hours_interval)
    
    logger.info(f"Generating {len(time_points)} measurements for zone {zone.id} ({zone.name})")
    
    # 推断生态系统类型
    ecosystem_type = infer_ecosystem_type(zone)
    
    # 批量生成数据
    measurements = []
    previous_ndvi = None
    
    for i, timestamp in enumerate(time_points):
        ndvi, carbon_absorption = generate_measurement_at_time(
            zone, timestamp, previous_ndvi, ecosystem_type
        )
        previous_ndvi = ndvi
        
        measurements.append({
            'zone_id': zone.id,
            'ndvi': ndvi,
            'carbon_absorption': carbon_absorption,
            'timestamp': timestamp
        })
        
        # 每100条记录批量插入一次
        if len(measurements) >= 100:
            db.bulk_insert_mappings(ZoneMeasurement, measurements)
            db.commit()
            measurements = []
            if (i + 1) % 500 == 0:
                logger.info(f"Generated {i + 1}/{len(time_points)} measurements for zone {zone.id}")
    
    # 插入剩余数据
    if measurements:
        db.bulk_insert_mappings(ZoneMeasurement, measurements)
        db.commit()
    
    total_generated = len(time_points)
    logger.info(f"Generated {total_generated} historical measurements for zone {zone.id}")
    return total_generated


def generate_historical_measurements_for_all_zones(
    days: int = 180,
    hours_interval: int = 12,
    force_regenerate: bool = False,
    zone_ids: Optional[List[int]] = None
) -> dict:
    """
    为所有活跃的监测区生成历史数据
    
    Args:
        days: 生成多少天的历史数据
        hours_interval: 测量间隔（小时）
        force_regenerate: 是否强制重新生成
        zone_ids: 指定区域ID列表，如果为None则处理所有活跃区域
    
    Returns:
        生成结果统计
    """
    db = SessionLocal()
    try:
        query = db.query(CarbonZone).filter(CarbonZone.status == ZoneStatus.active)
        if zone_ids:
            query = query.filter(CarbonZone.id.in_(zone_ids))
        
        active_zones = query.all()
        
        if not active_zones:
            logger.info("No active zones found")
            return {'total_zones': 0, 'total_measurements': 0, 'zones': {}}
        
        results = {
            'total_zones': len(active_zones),
            'total_measurements': 0,
            'zones': {}
        }
        
        for zone in active_zones:
            try:
                count = generate_historical_measurements_for_zone(
                    db, zone, days, hours_interval, force_regenerate
                )
                results['zones'][zone.id] = {
                    'name': zone.name,
                    'measurements_generated': count
                }
                results['total_measurements'] += count
            except Exception as e:
                logger.error(f"Error generating historical data for zone {zone.id}: {e}")
                results['zones'][zone.id] = {
                    'name': zone.name,
                    'error': str(e)
                }
        
        logger.info(f"Generated historical data: {results['total_measurements']} measurements for {results['total_zones']} zones")
        return results
        
    except Exception as e:
        logger.error(f"Error in generate_historical_measurements_for_all_zones: {e}")
        raise
    finally:
        db.close()


# ==================== 原有函数（增强版）====================

def generate_mock_measurement_for_zone(db: Session, zone: CarbonZone, timestamp: Optional[datetime] = None) -> ZoneMeasurement:
    """
    为指定区域生成模拟监测数据（增强版，保持向后兼容）
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    # 获取该区域的最新测量数据
    latest_measurement = db.query(ZoneMeasurement).filter(
        ZoneMeasurement.zone_id == zone.id
    ).order_by(ZoneMeasurement.timestamp.desc()).first()
    
    previous_ndvi = latest_measurement.ndvi if latest_measurement else None
    
    # 使用增强的生成函数
    ndvi, carbon_absorption = generate_measurement_at_time(
        zone, timestamp, previous_ndvi
    )
    
    measurement = ZoneMeasurement(
        zone_id=zone.id,
        ndvi=ndvi,
        carbon_absorption=carbon_absorption,
        timestamp=timestamp
    )
    
    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    
    logger.info(f"Generated measurement for zone {zone.id}: NDVI={ndvi:.4f}, Carbon={carbon_absorption:.6f}")
    return measurement


def generate_measurements_for_active_zones():
    """为所有活跃的监测区生成模拟监测数据"""
    # #region agent log
    import json, time, urllib.request, traceback
    def _agent_log(payload):
        try:
            urllib.request.urlopen(
                urllib.request.Request(
                    "http://host.docker.internal:7242/ingest/2b967610-c5aa-4d90-8694-335f6e0cdb1b",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                ),
                timeout=0.5,
            )
        except Exception:
            pass
    try:
        stack = traceback.extract_stack()
        caller = stack[-3].name if len(stack) >= 3 else "unknown"
    except Exception:
        caller = "unknown"
    _agent_log({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"backend/app/services/measurement_generator.py:generate_measurements_for_active_zones","message":"generate_measurements_for_active_zones called","data":{"caller":caller},"timestamp":int(time.time()*1000)})
    # #endregion
    db = SessionLocal()
    try:
        # 获取所有活跃的监测区
        active_zones = db.query(CarbonZone).filter(
            CarbonZone.status == ZoneStatus.active
        ).all()
        # #region agent log
        _agent_log({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"backend/app/services/measurement_generator.py:generate_measurements_for_active_zones","message":"Active zones found","data":{"active_zone_count":len(active_zones),"zone_ids":[z.id for z in active_zones]},"timestamp":int(time.time()*1000)})
        # #endregion

        if not active_zones:
            logger.info("No active zones found, skipping measurement generation")
            return

        generated_count = 0
        for zone in active_zones:
            try:
                generate_mock_measurement_for_zone(db, zone)
                generated_count += 1
            except Exception as e:
                logger.error(f"Error generating measurement for zone {zone.id}: {e}")

        logger.info(f"Generated measurements for {generated_count} active zones")
        # #region agent log
        _agent_log({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"backend/app/services/measurement_generator.py:generate_measurements_for_active_zones","message":"generate_measurements_for_active_zones completed","data":{"generated_count":generated_count},"timestamp":int(time.time()*1000)})
        # #endregion
    except Exception as e:
        logger.error(f"Error in generate_measurements_for_active_zones: {e}")
    finally:
        db.close()
