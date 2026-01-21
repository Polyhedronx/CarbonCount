from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from ..core.database import Base


class CarbonPrice(Base):
    __tablename__ = "carbon_prices"

    id = Column(Integer, primary_key=True, index=True)
    price = Column(Float, nullable=False)  # 价格（元/吨）
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    source = Column(String(100), nullable=False)  # 数据来源

    def __repr__(self):
        return f"<CarbonPrice(id={self.id}, price={self.price}, timestamp={self.timestamp})>"