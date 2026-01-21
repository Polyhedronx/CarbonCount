from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models import CarbonPrice
from ..schemas import CarbonPrice as CarbonPriceSchema
from ..services.price_service import get_current_price, generate_mock_price

router = APIRouter()


@router.get("/current")
async def get_current_carbon_price(db: Session = Depends(get_db)):
    """获取当前碳汇价格"""
    price = get_current_price(db)
    if not price:
        # 如果没有价格数据，生成模拟数据
        price = generate_mock_price(db)

    return {
        "price": price.price,
        "timestamp": price.timestamp,
        "source": price.source
    }


@router.get("/history", response_model=List[CarbonPriceSchema])
async def get_price_history(
    limit: int = 30,
    db: Session = Depends(get_db)
):
    """获取碳汇价格历史数据"""
    prices = db.query(CarbonPrice).order_by(
        CarbonPrice.timestamp.desc()
    ).limit(limit).all()

    return prices


@router.post("/generate-mock")
async def generate_mock_prices(db: Session = Depends(get_db)):
    """生成模拟价格数据（开发环境使用）"""
    price = generate_mock_price(db)
    return {
        "message": "Mock price generated",
        "price": price.price,
        "timestamp": price.timestamp
    }