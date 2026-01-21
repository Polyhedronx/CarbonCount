from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CarbonPriceBase(BaseModel):
    price: float = Field(..., gt=0, description="碳汇价格(元/吨)")
    source: str = Field(..., max_length=100, description="数据来源")


class CarbonPriceCreate(CarbonPriceBase):
    pass


class CarbonPrice(CarbonPriceBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class ZoneMeasurementBase(BaseModel):
    ndvi: float = Field(..., ge=0, le=1, description="归一化植被指数")
    carbon_absorption: float = Field(..., ge=0, description="碳吸收量(吨/天)")


class ZoneMeasurementCreate(ZoneMeasurementBase):
    zone_id: int


class ZoneMeasurement(ZoneMeasurementBase):
    id: int
    zone_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# 数据可视化相关
class MeasurementChartData(BaseModel):
    timestamps: List[datetime]
    ndvi_values: List[float]
    carbon_values: List[float]


class ZoneStats(BaseModel):
    total_carbon_absorption: float
    average_ndvi: float
    measurements_count: int
    latest_measurement: Optional[ZoneMeasurement] = None