import random
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..models import CarbonZone, ZoneMeasurement, ZoneStatus

logger = logging.getLogger(__name__)


def generate_mock_measurement_for_zone(db: Session, zone: CarbonZone) -> ZoneMeasurement:
    """为指定区域生成模拟监测数据"""
    # 获取该区域的最新测量数据，用于生成连续的数据
    latest_measurement = db.query(ZoneMeasurement).filter(
        ZoneMeasurement.zone_id == zone.id
    ).order_by(ZoneMeasurement.timestamp.desc()).first()

    # 基于最新数据生成新数据，如果没有则生成初始数据
    if latest_measurement:
        # NDVI在0.3-0.9之间波动，基于最新值小幅变化
        base_ndvi = latest_measurement.ndvi
        ndvi_change = random.uniform(-0.05, 0.05)
        ndvi = max(0.3, min(0.9, base_ndvi + ndvi_change))
        
        # 碳吸收量基于NDVI和面积计算，在0.0001-0.001吨/天之间
        base_carbon = latest_measurement.carbon_absorption
        carbon_change = random.uniform(-0.0001, 0.0001)
        carbon_absorption = max(0.0001, min(0.001, base_carbon + carbon_change))
    else:
        # 初始数据
        ndvi = random.uniform(0.4, 0.8)
        # 碳吸收量基于NDVI和面积，面积越大吸收越多
        base_carbon = (ndvi - 0.3) * 0.001 * (zone.area / 10000)  # 每公顷的碳吸收量
        carbon_absorption = max(0.0001, min(0.001, base_carbon + random.uniform(-0.00005, 0.00005)))

    measurement = ZoneMeasurement(
        zone_id=zone.id,
        ndvi=round(ndvi, 4),
        carbon_absorption=round(carbon_absorption, 6)
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
