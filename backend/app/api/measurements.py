from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.dependencies import get_current_user
from ..models import ZoneMeasurement, CarbonZone, User
from ..schemas import ZoneMeasurement, ZoneMeasurementCreate, MeasurementChartData
from ..services.measurement_service import get_zone_measurements_chart_data

router = APIRouter()


@router.get("/zone/{zone_id}", response_model=List[ZoneMeasurement])
async def get_zone_measurements(
    zone_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取碳汇监测区的测量数据"""
    # 验证用户权限
    zone = db.query(CarbonZone).filter(
        CarbonZone.id == zone_id,
        CarbonZone.user_id == current_user.id
    ).first()

    if not zone:
        raise HTTPException(
            status_code=404,
            detail="Zone not found or access denied"
        )

    measurements = db.query(ZoneMeasurement).filter(
        ZoneMeasurement.zone_id == zone_id
    ).order_by(ZoneMeasurement.timestamp.desc()).offset(skip).limit(limit).all()

    return measurements


@router.get("/zone/{zone_id}/chart", response_model=MeasurementChartData)
async def get_zone_chart_data(
    zone_id: int,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取碳汇监测区的图表数据"""
    # 验证用户权限
    zone = db.query(CarbonZone).filter(
        CarbonZone.id == zone_id,
        CarbonZone.user_id == current_user.id
    ).first()

    if not zone:
        raise HTTPException(
            status_code=404,
            detail="Zone not found or access denied"
        )

    chart_data = get_zone_measurements_chart_data(db, zone_id, limit)
    return chart_data


@router.post("/", response_model=ZoneMeasurement)
async def create_measurement(
    measurement_data: ZoneMeasurementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建测量数据（主要用于数据生成服务）"""
    # 验证用户权限
    zone = db.query(CarbonZone).filter(
        CarbonZone.id == measurement_data.zone_id,
        CarbonZone.user_id == current_user.id
    ).first()

    if not zone:
        raise HTTPException(
            status_code=404,
            detail="Zone not found or access denied"
        )

    db_measurement = ZoneMeasurement(
        zone_id=measurement_data.zone_id,
        ndvi=measurement_data.ndvi,
        carbon_absorption=measurement_data.carbon_absorption
    )

    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement