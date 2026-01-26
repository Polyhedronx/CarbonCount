from typing import List
import json
import logging
import threading
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from shapely.geometry import Polygon
from ..core.database import get_db, SessionLocal
from ..core.dependencies import get_current_user
from ..models import CarbonZone as CarbonZoneModel, ZoneStatus, User
from ..schemas import (
    CarbonZoneCreate,
    CarbonZoneUpdate,
    CarbonZone as CarbonZoneSchema,
    CarbonZoneWithMeasurements,
)
from ..services.measurement_service import get_zone_stats
from ..services.measurement_generator import generate_historical_measurements_for_zone

logger = logging.getLogger(__name__)

router = APIRouter()


def _parse_coords(zone: CarbonZoneModel) -> List[dict]:
    """将数据库中的坐标字符串解析为列表"""
    try:
        return json.loads(zone.coordinates)
    except Exception:
        return []


@router.get("/", response_model=List[CarbonZoneWithMeasurements])
async def get_zones(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的碳汇监测区列表"""
    zones = (
        db.query(CarbonZoneModel)
        .filter(CarbonZoneModel.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for zone in zones:
        stats = get_zone_stats(db, zone.id)
        zone_data = CarbonZoneWithMeasurements(
            id=zone.id,
            name=zone.name,
            coordinates=_parse_coords(zone),
            area=zone.area,
            status=zone.status,
            created_at=zone.created_at,
            user_id=zone.user_id,
            total_carbon_absorption=stats.total_carbon_absorption,
            current_ndvi=stats.average_ndvi,
            measurements_count=stats.measurements_count,
        )
        result.append(zone_data)

    return result


@router.post("/", response_model=CarbonZoneSchema)
async def create_zone(
    zone_data: CarbonZoneCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建碳汇监测区"""
    # 验证坐标点数量
    if len(zone_data.coordinates) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum 3 coordinate points required"
        )
    if len(zone_data.coordinates) > 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 7 coordinate points allowed"
        )

    # 计算面积
    coords = [(coord.lng, coord.lat) for coord in zone_data.coordinates]
    try:
        polygon = Polygon(coords)
        area = polygon.area * 111319.5 * 111319.5  # 转换为平方米（近似计算）
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coordinates"
        )

    # 创建监测区
    coords_json = [{"lat": coord.lat, "lng": coord.lng} for coord in zone_data.coordinates]
    db_zone = CarbonZoneModel(
        name=zone_data.name,
        coordinates=json.dumps(coords_json),  # 存储为JSON字符串
        area=area,
        user_id=current_user.id,
        status=ZoneStatus.active
    )

    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)

    # 在后台异步生成历史数据（不阻塞API响应）
    def generate_history_in_background(zone_id: int):
        """在后台线程中生成历史数据"""
        try:
            background_db = SessionLocal()
            try:
                zone = background_db.query(CarbonZoneModel).filter(
                    CarbonZoneModel.id == zone_id
                ).first()
                if zone:
                    logger.info(f"Starting historical data generation for new zone {zone_id}")
                    count = generate_historical_measurements_for_zone(
                        background_db, zone, days=180, hours_interval=12, force_regenerate=False
                    )
                    logger.info(f"Generated {count} historical measurements for zone {zone_id}")
                else:
                    logger.warning(f"Zone {zone_id} not found for historical data generation")
            except Exception as e:
                logger.error(f"Error generating historical data for zone {zone_id}: {e}")
            finally:
                background_db.close()
        except Exception as e:
            logger.error(f"Error in background thread for zone {zone_id}: {e}")
    
    # 启动后台线程生成历史数据
    thread = threading.Thread(
        target=generate_history_in_background,
        args=(db_zone.id,),
        daemon=True
    )
    thread.start()
    logger.info(f"Started background thread to generate historical data for zone {db_zone.id}")

    # 返回时将坐标字符串解析为列表，避免Pydantic校验错误
    return CarbonZoneSchema(
        id=db_zone.id,
        name=db_zone.name,
        coordinates=coords_json,
        area=db_zone.area,
        status=db_zone.status,
        created_at=db_zone.created_at,
        user_id=db_zone.user_id,
    )


@router.get("/{zone_id}", response_model=CarbonZoneWithMeasurements)
async def get_zone(
    zone_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个碳汇监测区"""
    zone = db.query(CarbonZoneModel).filter(
        CarbonZoneModel.id == zone_id,
        CarbonZoneModel.user_id == current_user.id
    ).first()

    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found"
        )

    stats = get_zone_stats(db, zone.id)
    return CarbonZoneWithMeasurements(
        id=zone.id,
        name=zone.name,
        coordinates=_parse_coords(zone),
        area=zone.area,
        status=zone.status,
        created_at=zone.created_at,
        user_id=zone.user_id,
        total_carbon_absorption=stats.total_carbon_absorption,
        current_ndvi=stats.average_ndvi,
        measurements_count=stats.measurements_count,
    )


@router.put("/{zone_id}", response_model=CarbonZoneSchema)
async def update_zone(
    zone_id: int,
    zone_update: CarbonZoneUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新碳汇监测区"""
    zone = db.query(CarbonZoneModel).filter(
        CarbonZoneModel.id == zone_id,
        CarbonZoneModel.user_id == current_user.id
    ).first()

    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found"
        )

    # 更新字段
    update_data = zone_update.model_dump(exclude_unset=True)
    if "coordinates" in update_data:
        coords = update_data["coordinates"]
        if len(coords) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum 3 coordinate points required"
            )
        if len(coords) > 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 7 coordinate points allowed"
            )
        # 重新计算面积
        coord_tuples = [(coord.lng, coord.lat) for coord in coords]
        try:
            polygon = Polygon(coord_tuples)
            update_data["area"] = polygon.area * 111319.5 * 111319.5
            coords_json = [{"lat": c.lat, "lng": c.lng} for c in coords]
            update_data["coordinates"] = json.dumps(coords_json)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid coordinates"
            )
    if "status" in update_data:
        update_data["status"] = ZoneStatus(update_data["status"])

    for field, value in update_data.items():
        setattr(zone, field, value)

    db.commit()
    db.refresh(zone)
    return CarbonZoneSchema(
        id=zone.id,
        name=zone.name,
        coordinates=_parse_coords(zone),
        area=zone.area,
        status=zone.status,
        created_at=zone.created_at,
        user_id=zone.user_id,
    )


@router.delete("/{zone_id}")
async def delete_zone(
    zone_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除碳汇监测区"""
    zone = db.query(CarbonZoneModel).filter(
        CarbonZoneModel.id == zone_id,
        CarbonZoneModel.user_id == current_user.id
    ).first()

    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found"
        )

    db.delete(zone)
    db.commit()
    return {"message": "Zone deleted successfully"}