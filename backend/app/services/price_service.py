import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import CarbonPrice


def get_current_price(db: Session) -> CarbonPrice:
    """获取最新的碳汇价格"""
    return db.query(CarbonPrice).order_by(CarbonPrice.timestamp.desc()).first()


def generate_mock_price(db: Session) -> CarbonPrice:
    """生成模拟碳汇价格数据"""
    # 基础价格在50-100元/吨之间波动
    base_price = 75.0
    variation = random.uniform(-15, 15)
    price = max(30, base_price + variation)  # 确保不低于30元

    db_price = CarbonPrice(
        price=round(price, 2),
        source="Mock Data Service"
    )

    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price


def generate_historical_prices(db: Session, days: int = 30):
    """生成历史价格数据"""
    prices = []
    base_price = 75.0

    for i in range(days):
        timestamp = datetime.utcnow() - timedelta(days=i)
        variation = random.uniform(-20, 20)
        price = max(30, base_price + variation)

        db_price = CarbonPrice(
            price=round(price, 2),
            timestamp=timestamp,
            source="Mock Historical Data"
        )
        prices.append(db_price)
        db.add(db_price)

    db.commit()
    return prices