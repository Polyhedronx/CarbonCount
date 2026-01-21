from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "postgresql://carbonuser:carbonpass123@localhost:5432/carboncount"

    # JWT配置
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 1天

    # 应用配置
    environment: str = "development"
    debug: bool = True

    # CORS配置
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # 地图配置
    default_map_center: list = [22.5828, 113.9686]  # 深圳大学粤海校区
    default_map_zoom: int = 16

    # 碳汇价格API (暂时使用mock)
    carbon_price_api_url: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()