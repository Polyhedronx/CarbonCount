from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class ZoneMeasurement(Base):
    __tablename__ = "zone_measurements"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("carbon_zones.id"), nullable=False)
    ndvi = Column(Float, nullable=False)  # 归一化植被指数
    carbon_absorption = Column(Float, nullable=False)  # 碳吸收量（吨/天）
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # 关联关系
    carbon_zone = relationship("CarbonZone", back_populates="measurements")

    def __repr__(self):
        return f"<ZoneMeasurement(id={self.id}, zone_id={self.zone_id}, ndvi={self.ndvi:.4f}, carbon_absorption={self.carbon_absorption:.6f})>"