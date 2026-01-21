# 导入所有模型
from .user import User, UserRole
from .carbon_zone import CarbonZone, ZoneStatus
from .carbon_price import CarbonPrice
from .zone_measurement import ZoneMeasurement

# 确保所有模型都被注册到Base.metadata
from ..core.database import Base

# 创建所有表（用于初始化）
def create_tables():
    Base.metadata.create_all(bind=Base.metadata.bind)