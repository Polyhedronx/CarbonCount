from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import ZoneMeasurement
from ..schemas import ZoneStats


def get_zone_stats(db: Session, zone_id: int) -> ZoneStats:
    """获取碳汇监测区的统计数据"""
    # 查询该区域的所有测量数据
    measurements = db.query(ZoneMeasurement).filter(ZoneMeasurement.zone_id == zone_id).all()

    if not measurements:
        return ZoneStats(
            total_carbon_absorption=0.0,
            average_ndvi=0.0,
            measurements_count=0,
            latest_measurement=None
        )

    # 计算统计数据
    total_carbon = sum(m.carbon_absorption for m in measurements)
    avg_ndvi = sum(m.ndvi for m in measurements) / len(measurements)
    latest_measurement = max(measurements, key=lambda m: m.timestamp)

    return ZoneStats(
        total_carbon_absorption=round(total_carbon, 6),
        average_ndvi=round(avg_ndvi, 4),
        measurements_count=len(measurements),
        latest_measurement=latest_measurement
    )


def get_zone_measurements_chart_data(db: Session, zone_id: int, limit: int = 100):
    """获取区域测量数据的图表数据"""
    measurements = db.query(ZoneMeasurement).filter(
        ZoneMeasurement.zone_id == zone_id
    ).order_by(ZoneMeasurement.timestamp.desc()).limit(limit).all()

    # 反转以按时间正序排列
    measurements.reverse()

    return {
        "timestamps": [m.timestamp for m in measurements],
        "ndvi_values": [m.ndvi for m in measurements],
        "carbon_values": [m.carbon_absorption for m in measurements]
    }