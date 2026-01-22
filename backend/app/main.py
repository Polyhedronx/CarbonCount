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
from .services.price_service import update_price_hourly

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据库表
Base.metadata.create_all(bind=engine)


def run_scheduler():
    """运行定时任务调度器"""
    # #region agent log
    import json, time, urllib.request
    def _agent_log(payload):
        try:
            urllib.request.urlopen(
                urllib.request.Request(
                    "http://host.docker.internal:7242/ingest/2b967610-c5aa-4d90-8694-335f6e0cdb1b",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                ),
                timeout=0.5,
            )
        except Exception:
            pass
    _agent_log({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"backend/app/main.py:run_scheduler","message":"run_scheduler called","data":{},"timestamp":int(time.time()*1000)})
    # #endregion
    # 每12小时生成一次监测数据（每天2次）
    schedule.every(12).hours.do(generate_measurements_for_active_zones)
    # #region agent log
    try:
        jobs = schedule.get_jobs()
        _agent_log({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"backend/app/main.py:run_scheduler","message":"Schedule jobs registered (after measurement job)","data":{"job_count":len(jobs)},"timestamp":int(time.time()*1000)})
    except Exception:
        pass
    # #endregion
    
    # 每小时更新一次碳汇价格
    schedule.every().hour.do(update_price_hourly)
    
    logger.info("Measurement data scheduler started (runs every 12 hours, twice per day)")
    logger.info("Price update scheduler started (runs every hour)")
    
    while True:
        schedule.run_pending()
        import time
        time.sleep(60)  # 每分钟检查一次


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Starting CarbonCount API...")
    # #region agent log
    import json, time, urllib.request
    def _agent_log(payload):
        try:
            urllib.request.urlopen(
                urllib.request.Request(
                    "http://host.docker.internal:7242/ingest/2b967610-c5aa-4d90-8694-335f6e0cdb1b",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                ),
                timeout=0.5,
            )
        except Exception:
            pass
    _agent_log({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"backend/app/main.py:lifespan","message":"lifespan startup called","data":{},"timestamp":int(time.time()*1000)})
    # #endregion
    
    # 启动后台任务线程
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Background scheduler thread started")
    
    # 注意：不再在启动时立即生成监测数据。
    # 监测数据应仅由定时任务（每12小时）生成，以避免重启服务时产生密集时间戳的数据。
    
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