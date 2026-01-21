import asyncio
import logging
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import schedule
from .core.database import engine, get_db
from .core.config import settings
from .core.security import verify_token
from .core.dependencies import get_current_user, get_current_admin
from .models import Base, User
from .api import auth, carbon_zones, measurements, prices
from .services.measurement_generator import generate_measurements_for_active_zones

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据库表
Base.metadata.create_all(bind=engine)


def run_scheduler():
    """运行定时任务调度器"""
    # 每6小时生成一次监测数据
    schedule.every(6).hours.do(generate_measurements_for_active_zones)
    
    logger.info("Measurement data scheduler started (runs every 6 hours)")
    
    while True:
        schedule.run_pending()
        import time
        time.sleep(60)  # 每分钟检查一次


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Starting CarbonCount API...")
    
    # 启动后台任务线程
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Background scheduler thread started")
    
    # 立即生成一次数据（用于测试）
    try:
        generate_measurements_for_active_zones()
    except Exception as e:
        logger.error(f"Error in initial measurement generation: {e}")
    
    yield
    
    # 关闭时
    logger.info("Shutting down CarbonCount API...")


# 创建FastAPI应用
app = FastAPI(
    title="CarbonCount API",
    description="碳汇监测Web应用API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["authentication"]
)

app.include_router(
    carbon_zones.router,
    prefix="/api/zones",
    tags=["carbon-zones"]
)

app.include_router(
    measurements.router,
    prefix="/api/measurements",
    tags=["measurements"]
)

app.include_router(
    prices.router,
    prefix="/api/prices",
    tags=["prices"]
)

@app.get("/")
async def root():
    return {"message": "CarbonCount API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}