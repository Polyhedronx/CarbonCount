from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import json
from ..core.database import Base


class ZoneStatus(str, enum.Enum):
    active = "active"      # 监测中
    inactive = "inactive"  # 停止监测


class CarbonZone(Base):
    __tablename__ = "carbon_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False)  # 2-20字符
    coordinates = Column(Text, nullable=False)  # JSON格式的坐标数组
    area = Column(Float, nullable=False)  # 面积（平方米）
    status = Column(Enum(ZoneStatus), default=ZoneStatus.active, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 关联关系
    user = relationship("User", back_populates="carbon_zones")
    measurements = relationship("ZoneMeasurement", back_populates="carbon_zone", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CarbonZone(id={self.id}, name={self.name}, status={self.status}, area={self.area:.2f}m²)>"

    @property
    def coordinates_list(self):
        """获取坐标列表"""
        return json.loads(self.coordinates)

    @coordinates_list.setter
    def coordinates_list(self, coords):
        """设置坐标列表"""
        self.coordinates = json.dumps(coords)