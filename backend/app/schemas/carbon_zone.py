from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Coordinate(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="纬度")
    lng: float = Field(..., ge=-180, le=180, description="经度")


class CarbonZoneBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=20, description="监测区名称")
    coordinates: List[Coordinate] = Field(..., min_items=3, max_items=7, description="坐标点列表")
    area: float = Field(..., gt=0, description="面积(平方米)")


class CarbonZoneCreate(BaseModel):
    """创建监测区时不需要area字段，后端会自动计算"""
    name: str = Field(..., min_length=2, max_length=20, description="监测区名称")
    coordinates: List[Coordinate] = Field(..., min_items=3, max_items=7, description="坐标点列表")


class CarbonZoneUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=20)
    coordinates: Optional[List[Coordinate]] = Field(None, min_items=3, max_items=7)
    area: Optional[float] = Field(None, gt=0)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")


class CarbonZone(CarbonZoneBase):
    id: int
    status: str
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class CarbonZoneWithMeasurements(CarbonZone):
    total_carbon_absorption: Optional[float] = None
    current_ndvi: Optional[float] = None
    measurements_count: int = 0

    class Config:
        from_attributes = True