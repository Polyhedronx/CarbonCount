# 碳汇监测Web应用

基于FastAPI + Vue3/Vite + Docker + PostgreSQL开发的碳汇监测Web应用，用于创建和管理碳汇监测区，实时展示监测数据和碳汇价格信息。

## 项目结构

```
CarbonCount_Fastapi/
├── backend/                          # FastAPI后端
│   ├── app/
│   │   ├── api/                      # API路由层
│   │   │   ├── auth.py               # 认证相关API
│   │   │   ├── carbon_zones.py      # 监测区CRUD API
│   │   │   ├── measurements.py       # 监测数据查询API
│   │   │   └── prices.py             # 价格数据API
│   │   ├── core/                     # 核心配置模块
│   │   │   ├── config.py             # 应用配置
│   │   │   ├── database.py           # 数据库连接
│   │   │   ├── security.py           # 安全相关（JWT、密码加密）
│   │   │   └── dependencies.py       # 依赖注入
│   │   ├── models/                   # SQLAlchemy数据库模型
│   │   │   ├── user.py               # 用户模型
│   │   │   ├── carbon_zone.py        # 监测区模型
│   │   │   ├── zone_measurement.py   # 监测数据模型
│   │   │   └── carbon_price.py       # 价格数据模型
│   │   ├── schemas/                  # Pydantic数据验证模型
│   │   │   ├── user.py
│   │   │   ├── carbon_zone.py
│   │   │   └── measurement.py
│   │   ├── services/                 # 业务逻辑层
│   │   │   ├── measurement_service.py    # 监测数据业务逻辑
│   │   │   ├── price_service.py          # 价格数据业务逻辑
│   │   │   └── measurement_generator.py  # 自动生成监测数据服务
│   │   ├── utils/                    # 工具函数
│   │   └── main.py                   # 应用入口
│   ├── Dockerfile
│   ├── init.sql                      # 数据库初始化SQL
│   └── requirements.txt
├── frontend/                         # Vue3前端
│   ├── src/
│   │   ├── api/                      # API调用模块
│   │   │   ├── auth.js
│   │   │   ├── zones.js
│   │   │   ├── measurements.js
│   │   │   └── prices.js
│   │   ├── components/               # Vue组件
│   │   │   ├── MapView.vue           # 地图视图
│   │   │   ├── ZoneList.vue          # 监测区列表
│   │   │   ├── ControlPanel.vue      # 控制面板
│   │   │   ├── PriceCard.vue         # 价格卡片
│   │   │   ├── UserProfile.vue       # 用户信息
│   │   │   ├── ZoneInfoCard.vue      # 监测区信息卡片
│   │   │   └── ZoneChartCard.vue     # 监测区图表卡片
│   │   ├── views/                    # 页面视图
│   │   │   ├── Login.vue             # 登录页面
│   │   │   ├── Dashboard.vue         # 主仪表板
│   │   │   └── ZoneDetail.vue        # 监测区详情页
│   │   ├── stores/                   # Pinia状态管理
│   │   │   └── auth.js
│   │   ├── router/                   # 路由配置
│   │   │   └── index.js
│   │   ├── composables/              # 组合式函数
│   │   │   ├── useChartConfig.js
│   │   │   ├── usePDFExport.js
│   │   │   └── useZoneDetail.js
│   │   ├── utils/                    # 工具函数
│   │   │   └── formatters.js
│   │   ├── App.vue
│   │   └── main.js
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
├── web/                              # Nginx Web服务
│   └── Dockerfile
├── docs/                             # 文档目录
│   ├── architecture.md               # 架构文档
│   ├── deployment.md                 # 部署文档
│   └── database_verification.md      # 数据库验证指南
├── scripts/                           # 脚本目录
│   ├── verify-database.ps1           # 数据库验证脚本
│   └── quick-verify.md
├── docker-compose.yml                 # Docker编排配置
└── README.md
```

## 技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 开发语言 |
| FastAPI | 0.104.1 | Web框架 |
| SQLAlchemy | 2.0.23 | ORM框架 |
| PostgreSQL | 15 | 关系型数据库 |
| Pydantic | 2.5.0 | 数据验证 |
| python-jose | 3.3.0 | JWT认证 |
| passlib | 1.7.4 | 密码加密 |
| Shapely | 2.0.2 | 地理计算 |
| Schedule | 1.2.1 | 定时任务 |
| Uvicorn | 0.24.0 | ASGI服务器 |

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue.js | 3.3.0 | 前端框架 |
| Vite | 4.3.0 | 构建工具 |
| Vue Router | 4.2.0 | 路由管理 |
| Pinia | 2.1.0 | 状态管理 |
| Element Plus | 2.3.0 | UI组件库 |
| Leaflet | 1.9.0 | 地图库 |
| ECharts | 5.4.0 | 图表库 |
| Vue-ECharts | 6.6.0 | ECharts Vue封装 |
| Axios | 1.4.0 | HTTP客户端 |

### 部署

- **Docker**: 容器化
- **Docker Compose**: 多容器编排
- **Nginx**: 反向代理和静态文件服务

## 快速开始

### 环境要求

- Docker
- Docker Compose

### 启动应用

1. 克隆项目

```bash
git clone <repository-url>
cd CarbonCount_Fastapi
```

2. 启动所有服务

```bash
docker-compose up -d
```

3. 等待服务启动完成后，访问应用

- **前端应用**: http://localhost:3000
- **后端API文档**: http://localhost:8001/docs (Swagger UI)
- **后端API文档**: http://localhost:8001/redoc (ReDoc)
- **后端API**: http://localhost:8001/api

### 默认管理员账号

- 用户名: `admin`
- 密码: `Admin123`

## 功能特性

### 用户系统

- [x] 用户注册/登录
- [x] JWT认证
- [x] 角色权限管理（管理员/普通用户）

### 地图功能

- [x] 高德地图集成
- [x] 深圳大学粤海校区初始位置
- [x] 创建碳汇监测区（最多7个点）
- [x] 区域编辑和管理

### 数据管理

- [x] 碳汇监测区CRUD操作
- [x] 实时碳汇价格展示
- [x] 监测数据存储和查询

### 界面设计

- [x] 响应式Dashboard布局
- [x] 左侧控制面板
- [x] 个人中心集成

### 高级功能

- [x] 监测数据自动生成服务（每6小时自动生成）
- [x] NDVI和碳吸收量历史图表
- [x] 区域数据导出功能（PDF导出）
- [x] 监测区详情页面
- [x] 实时价格展示

## API接口

### 基础信息

- **基础URL**: `http://localhost:8001/api`
- **认证方式**: JWT Bearer Token
- **请求格式**: JSON
- **响应格式**: JSON

### 认证接口 (`/api/auth`)

- `POST /api/auth/register` - 用户注册
  ```json
  Request: {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```

- `POST /api/auth/login` - 用户登录
  ```json
  Request: {
    "username": "string",
    "password": "string"
  }
  Response: {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  }
  ```

### 监测区接口 (`/api/zones`)

- `GET /api/zones/` - 获取当前用户的监测区列表（需认证）
- `POST /api/zones/` - 创建监测区（需认证）
  ```json
  Request: {
    "name": "string",
    "coordinates": [[22.5828, 113.9686], ...],
    "area": 1234.56
  }
  ```
- `GET /api/zones/{zone_id}` - 获取单个监测区详情（需认证）
- `PUT /api/zones/{zone_id}` - 更新监测区（需认证）
- `DELETE /api/zones/{zone_id}` - 删除监测区（需认证，级联删除监测数据）

### 监测数据接口 (`/api/measurements`)

- `GET /api/measurements/zone/{zone_id}` - 获取区域监测数据列表（需认证）
  - 查询参数: `limit` (默认100), `offset`
- `GET /api/measurements/zone/{zone_id}/chart` - 获取图表数据（时间序列格式，需认证）
- `POST /api/measurements/` - 创建监测数据（需认证）
  ```json
  Request: {
    "zone_id": 1,
    "ndvi": 0.75,
    "carbon_absorption": 12.5
  }
  ```

### 价格接口 (`/api/prices`)

- `GET /api/prices/current` - 获取当前碳汇价格
- `GET /api/prices/history` - 获取价格历史记录
  - 查询参数: `limit` (默认100)
- `POST /api/prices/generate-mock` - 生成模拟价格数据（仅管理员）

> 更多API详情请访问 http://localhost:8001/docs 查看完整的Swagger文档

## 开发指南

### 环境要求

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.11+ (本地开发)
- **Node.js**: 18+ (本地开发)

### 使用Docker开发（推荐）

1. **启动所有服务**
   ```bash
   docker-compose up -d
   ```

2. **查看日志**
   ```bash
   # 查看所有服务日志
   docker-compose logs -f
   
   # 查看特定服务日志
   docker-compose logs -f backend
   docker-compose logs -f web
   ```

3. **重启服务**
   ```bash
   docker-compose restart backend
   docker-compose restart web
   ```

4. **停止服务**
   ```bash
   docker-compose down
   ```

### 本地开发

#### 后端开发

1. **环境设置**
   ```bash
   cd backend
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   
   创建 `.env` 文件（或设置环境变量）：
   ```env
   DATABASE_URL=postgresql://carbonuser:carbonpass123@localhost:5433/carboncount
   SECRET_KEY=your-secret-key-change-in-production
   ENVIRONMENT=development
   ```

3. **启动开发服务器**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **访问API文档**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

#### 前端开发

1. **环境设置**
   ```bash
   cd frontend
   npm install
   ```

2. **启动开发服务器**
   ```bash
   npm run dev
   ```

3. **访问前端应用**
   - 开发服务器: http://localhost:5173 (Vite默认端口)

4. **构建生产版本**
   ```bash
   npm run build
   ```

### 数据库操作

#### 连接数据库

```bash
# 通过Docker进入数据库容器
docker-compose exec db psql -U carbonuser -d carboncount
```

#### 数据库信息

- **数据库类型**: PostgreSQL
- **数据库名**: `carboncount`
- **用户名**: `carbonuser`
- **密码**: `carbonpass123`
- **容器内端口**: `5432`
- **外部端口**: `5433`

#### 数据库表结构

- `users` - 用户表
- `carbon_zones` - 监测区表
- `zone_measurements` - 监测数据表
- `carbon_prices` - 价格表

> 数据库表会在应用启动时自动创建。更多数据库操作请参考 `docs/database_verification.md`

## 部署说明

### 生产环境

1. 修改环境变量
2. 更新Docker配置
3. 使用生产级数据库
4. 配置反向代理

### 监控和日志

- 应用日志输出到容器日志
- API响应时间监控
- 错误异常记录
