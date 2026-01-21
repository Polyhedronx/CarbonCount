# 碳汇监测系统 - 代码架构文档

## 目录

- [项目概述](#项目概述)
- [技术栈](#技术栈)
- [项目目录结构](#项目目录结构)
- [后端架构](#后端架构)
- [前端架构](#前端架构)
- [数据库设计](#数据库设计)
- [API接口设计](#api接口设计)
- [核心功能模块](#核心功能模块)
- [开发工作流](#开发工作流)
- [部署架构](#部署架构)

---

## 项目概述

CarbonCount 是一个基于 FastAPI + Vue3 开发的碳汇监测Web应用，用于创建和管理碳汇监测区，实时展示监测数据和碳汇价格信息。

### 核心功能

1. **用户认证系统** - JWT认证，支持用户注册/登录
2. **地图交互** - Leaflet地图，支持创建和管理监测区域
3. **数据可视化** - ECharts图表展示NDVI和碳吸收量趋势
4. **监测数据管理** - 自动生成和历史数据查询
5. **价格展示** - 实时碳汇价格和历史价格查询

---

## 技术栈

### 后端技术栈

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

### 前端技术栈

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
| Day.js | - | 日期处理 |

### 部署技术栈

| 技术 | 用途 |
|------|------|
| Docker | 容器化 |
| Docker Compose | 多容器编排 |
| Nginx | 反向代理和静态文件服务 |

---

## 项目目录结构

```
CarbonCount_Fastapi/
├── backend/                          # 后端代码目录
│   ├── app/                          # FastAPI应用主目录
│   │   ├── __init__.py
│   │   ├── main.py                   # 应用入口，路由注册
│   │   │
│   │   ├── api/                      # API路由层
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # 认证相关API（登录/注册）
│   │   │   ├── carbon_zones.py       # 监测区CRUD API
│   │   │   ├── measurements.py       # 监测数据查询API
│   │   │   └── prices.py             # 价格数据API
│   │   │
│   │   ├── core/                     # 核心配置模块
│   │   │   ├── config.py             # 应用配置（环境变量、数据库URL等）
│   │   │   ├── database.py           # 数据库连接和Session管理
│   │   │   ├── security.py           # 安全相关（JWT、密码加密）
│   │   │   └── dependencies.py       # 依赖注入（用户认证等）
│   │   │
│   │   ├── models/                   # SQLAlchemy数据库模型
│   │   │   ├── __init__.py           # 导出所有模型
│   │   │   ├── user.py               # 用户模型
│   │   │   ├── carbon_zone.py        # 监测区模型
│   │   │   ├── zone_measurement.py   # 监测数据模型
│   │   │   └── carbon_price.py       # 价格数据模型
│   │   │
│   │   ├── schemas/                  # Pydantic数据验证模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py               # 用户相关Schema
│   │   │   ├── carbon_zone.py        # 监测区相关Schema
│   │   │   └── measurement.py        # 监测数据相关Schema
│   │   │
│   │   ├── services/                 # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── measurement_service.py    # 监测数据业务逻辑
│   │   │   ├── price_service.py          # 价格数据业务逻辑
│   │   │   └── measurement_generator.py  # 自动生成监测数据服务
│   │   │
│   │   └── utils/                    # 工具函数
│   │       └── __init__.py
│   │
│   ├── Dockerfile                    # 后端Docker镜像构建文件
│   ├── init.sql                      # 数据库初始化SQL脚本
│   └── requirements.txt              # Python依赖包列表
│
├── frontend/                         # 前端代码目录
│   ├── src/                          # 源代码目录
│   │   ├── main.js                   # 应用入口文件
│   │   ├── App.vue                   # 根组件
│   │   │
│   │   ├── api/                      # API调用模块
│   │   │   ├── auth.js               # 认证相关API
│   │   │   ├── zones.js              # 监测区相关API
│   │   │   ├── measurements.js       # 监测数据相关API
│   │   │   └── prices.js             # 价格相关API
│   │   │
│   │   ├── components/               # Vue组件
│   │   │   ├── MapView.vue           # 地图视图组件
│   │   │   ├── ZoneList.vue          # 监测区列表组件
│   │   │   ├── ControlPanel.vue      # 控制面板组件
│   │   │   ├── PriceCard.vue         # 价格卡片组件
│   │   │   └── UserProfile.vue       # 用户信息组件
│   │   │
│   │   ├── views/                    # 页面视图
│   │   │   ├── Login.vue             # 登录页面
│   │   │   └── Dashboard.vue         # 主仪表板页面
│   │   │
│   │   ├── router/                   # 路由配置
│   │   │   └── index.js              # 路由定义和守卫
│   │   │
│   │   └── stores/                   # Pinia状态管理
│   │       └── auth.js               # 认证状态管理
│   │
│   ├── public/                       # 静态资源目录
│   ├── dist/                         # 构建输出目录
│   ├── package.json                  # 前端依赖配置
│   ├── vite.config.js                # Vite构建配置
│   └── Dockerfile                    # 前端Docker镜像构建文件
│
├── web/                              # Web服务配置（Nginx）
│   └── Dockerfile                    # Nginx容器构建文件
│
├── docs/                             # 文档目录
│   ├── architecture.md               # 架构文档（本文档）
│   ├── deployment.md                 # 部署文档
│   └── requirements.md               # 需求文档
│
├── docker-compose.yml                # Docker Compose编排配置
├── README.md                         # 项目说明文档
└── .env                              # 环境变量配置（可选，不提交到Git）
```

---

## 后端架构

### 架构设计模式

后端采用 **分层架构** 模式，清晰分离关注点：

```
┌─────────────────────────────────────┐
│        API Layer (api/)             │  路由层：处理HTTP请求/响应
├─────────────────────────────────────┤
│      Service Layer (services/)      │  业务逻辑层：核心业务处理
├─────────────────────────────────────┤
│       Model Layer (models/)         │  数据模型层：数据库ORM映射
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│     Database (PostgreSQL)           │  数据持久层
└─────────────────────────────────────┘
```

### 核心模块详解

#### 1. API层 (`app/api/`)

**职责**：处理HTTP请求，参数验证，调用Service层，返回响应

**文件结构**：
- `auth.py` - 用户认证相关接口
  - `POST /api/auth/register` - 用户注册
  - `POST /api/auth/login` - 用户登录
  
- `carbon_zones.py` - 监测区管理接口
  - `GET /api/zones/` - 获取用户监测区列表
  - `POST /api/zones/` - 创建监测区
  - `GET /api/zones/{zone_id}` - 获取单个监测区详情
  - `PUT /api/zones/{zone_id}` - 更新监测区
  - `DELETE /api/zones/{zone_id}` - 删除监测区

- `measurements.py` - 监测数据查询接口
  - `GET /api/measurements/zone/{zone_id}` - 获取区域监测数据列表
  - `GET /api/measurements/zone/{zone_id}/chart` - 获取图表数据（时间序列）
  - `POST /api/measurements/` - 创建监测数据（手动创建）

- `prices.py` - 价格数据接口
  - `GET /api/prices/current` - 获取当前碳汇价格
  - `GET /api/prices/history` - 获取价格历史记录
  - `POST /api/prices/generate-mock` - 生成模拟价格数据（管理员）

**设计要点**：
- 使用FastAPI的依赖注入系统（`Depends`）进行身份验证
- 通过Schema进行请求/响应数据的验证和序列化
- 统一错误处理和HTTP状态码

#### 2. Service层 (`app/services/`)

**职责**：封装业务逻辑，处理复杂计算，协调多个Model操作

**文件结构**：
- `measurement_service.py` - 监测数据业务逻辑
  - 数据聚合和统计
  - 时间序列数据格式化
  
- `price_service.py` - 价格数据业务逻辑
  - 价格查询和缓存
  - 模拟数据生成
  
- `measurement_generator.py` - 自动数据生成服务
  - 定时任务：每6小时生成一次监测数据
  - 为所有活跃的监测区生成NDVI和碳吸收量数据
  - 使用Faker生成随机但符合逻辑的数据

**设计要点**：
- 业务逻辑与API层解耦，便于测试和复用
- 使用异步操作处理耗时任务

#### 3. Model层 (`app/models/`)

**职责**：定义数据库表结构，ORM映射，数据关系

**核心模型**：

**User（用户模型）**
```python
- id: 主键
- username: 用户名（唯一索引）
- email: 邮箱
- password_hash: 密码哈希值
- role: 角色（admin/user）
- created_at: 创建时间
- is_active: 是否激活
- carbon_zones: 关联的监测区（一对多）
```

**CarbonZone（监测区模型）**
```python
- id: 主键
- name: 监测区名称（2-20字符）
- coordinates: 坐标JSON字符串
- area: 面积（平方米）
- status: 状态（active/inactive）
- created_at: 创建时间
- user_id: 用户ID（外键）
- user: 关联的用户（多对一）
- measurements: 关联的监测数据（一对多）
```

**ZoneMeasurement（监测数据模型）**
```python
- id: 主键
- zone_id: 监测区ID（外键）
- ndvi: NDVI值（归一化植被指数）
- carbon_absorption: 碳吸收量（吨/天）
- timestamp: 时间戳
- carbon_zone: 关联的监测区（多对一）
```

**CarbonPrice（价格模型）**
```python
- id: 主键
- price: 价格（元/吨）
- timestamp: 时间戳
- source: 数据来源
```

#### 4. Schema层 (`app/schemas/`)

**职责**：数据验证和序列化，定义API请求/响应格式

**设计要点**：
- 使用Pydantic进行数据验证
- 区分创建、更新、响应等不同场景的Schema
- 自动处理数据类型转换

#### 5. Core模块 (`app/core/`)

**config.py** - 应用配置管理
- 数据库连接字符串
- JWT密钥和过期时间
- CORS配置
- 环境变量管理（通过python-decouple）

**database.py** - 数据库连接管理
- SQLAlchemy引擎创建
- Session工厂配置
- 依赖注入函数 `get_db()`

**security.py** - 安全相关功能
- JWT Token生成和验证
- 密码加密和验证（passlib + bcrypt）
- Token解码

**dependencies.py** - 依赖注入函数
- `get_current_user()` - 获取当前登录用户
- `get_current_admin()` - 获取当前管理员用户

#### 6. 应用入口 (`app/main.py`)

**功能**：
- FastAPI应用实例创建
- CORS中间件配置
- 路由注册
- 应用生命周期管理（启动定时任务）

**生命周期管理**：
- 启动时：创建定时任务线程（每6小时生成监测数据）
- 关闭时：清理资源

---

## 前端架构

### 架构设计模式

前端采用 **组件化 + 状态管理** 的架构模式：

```
┌─────────────────────────────────────┐
│        Views (页面层)               │  页面组件：路由对应的完整页面
├─────────────────────────────────────┤
│     Components (组件层)             │  可复用组件：功能模块
├─────────────────────────────────────┤
│      Stores (状态层)                │  Pinia状态管理：全局状态
├─────────────────────────────────────┤
│       API Layer (api/)              │  API调用层：HTTP请求封装
└─────────────────────────────────────┘
```

### 核心模块详解

#### 1. 路由系统 (`src/router/index.js`)

**路由配置**：
- `/login` - 登录页面（无需认证）
- `/` - Dashboard主页面（需要认证）
- 默认重定向到 `/`

**路由守卫**：
- 检查用户认证状态
- 未认证用户访问受保护路由 → 重定向到登录页
- 已认证用户访问登录页 → 重定向到Dashboard

#### 2. 状态管理 (`src/stores/auth.js`)

**Pinia Store：认证状态管理**

**State（状态）**：
- `user` - 当前用户信息
- `token` - JWT Token
- `isAuthenticated` - 认证状态标识

**Actions（操作）**：
- `login(credentials)` - 用户登录，存储Token
- `register(userData)` - 用户注册
- `logout()` - 用户登出，清除Token
- `initializeAuth()` - 应用启动时初始化认证状态

**设计要点**：
- Token存储在localStorage中持久化
- 自动设置axios的Authorization Header
- 与路由守卫配合实现认证拦截

#### 3. API调用层 (`src/api/`)

**职责**：封装HTTP请求，统一处理错误

**文件结构**：
- `auth.js` - 认证相关API
- `zones.js` - 监测区相关API
- `measurements.js` - 监测数据相关API
- `prices.js` - 价格相关API

**设计要点**：
- 使用axios进行HTTP请求
- 统一的基础URL配置（通过Vite代理或Nginx反向代理）
- 自动携带JWT Token
- 统一错误处理

#### 4. 组件系统 (`src/components/`)

**MapView.vue** - 地图视图组件
- **功能**：Leaflet地图渲染和交互
- **主要功能**：
  - 地图初始化和显示
  - 监测区创建模式（点击地图添加点，最多7个点）
  - 监测区展示（多边形标记）
  - 监测区编辑（拖拽顶点）
  - 地图事件处理
- **Props**：
  - `zones` - 监测区列表
  - `createMode` - 是否处于创建模式
- **Emits**：
  - `zone-created` - 监测区创建完成
  - `zone-selected` - 监测区被选中

**ZoneList.vue** - 监测区列表组件
- **功能**：显示用户的所有监测区
- **主要功能**：
  - 监测区列表展示
  - 监测区详情（面积、创建时间、状态）
  - NDVI和碳吸收量图表展示
  - 监测区编辑/删除操作
- **数据来源**：通过API获取监测区列表和监测数据

**ControlPanel.vue** - 控制面板组件
- **功能**：左侧控制面板
- **主要功能**：
  - 实时价格显示
  - 创建监测区按钮
  - 完成创建按钮
  - 监测区列表容器

**PriceCard.vue** - 价格卡片组件
- **功能**：显示当前碳汇价格
- **数据来源**：实时调用价格API

**UserProfile.vue** - 用户信息组件
- **功能**：显示用户信息和登出功能
- **位置**：Dashboard左上角

#### 5. 页面视图 (`src/views/`)

**Login.vue** - 登录页面
- **功能**：用户登录和注册
- **表单验证**：Element Plus表单验证
- **功能切换**：登录/注册模式切换

**Dashboard.vue** - 主仪表板
- **布局**：
  - 左上角：UserProfile组件
  - 左侧：ControlPanel组件（包含PriceCard和ZoneList）
  - 右侧：MapView组件
- **状态管理**：
  - 监测区创建模式控制
  - 监测区列表数据
  - 当前选中监测区

#### 6. 主应用 (`src/main.js` 和 `App.vue`)

**main.js**：
- Vue应用初始化
- 路由注册
- Pinia状态管理注册
- Element Plus组件库引入
- 全局样式引入

**App.vue**：
- 根组件
- 仅包含 `<router-view />`
- 全局样式定义

---

## 数据库设计

### 数据库架构

使用 **PostgreSQL** 关系型数据库，通过SQLAlchemy ORM进行管理。

### 表结构详解

#### 1. users（用户表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 主键，自增 |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名，唯一 |
| email | VARCHAR(100) | NOT NULL | 邮箱地址 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希值（bcrypt） |
| role | ENUM | NOT NULL, DEFAULT 'user' | 用户角色（admin/user） |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | 是否激活 |

**索引**：
- `username` 唯一索引

**关联关系**：
- 一对多：`users` → `carbon_zones`（一个用户可以有多个监测区）

#### 2. carbon_zones（监测区表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 主键，自增 |
| name | VARCHAR(20) | NOT NULL | 监测区名称（2-20字符） |
| coordinates | TEXT | NOT NULL | JSON格式坐标数组 |
| area | FLOAT | NOT NULL | 面积（平方米） |
| status | ENUM | NOT NULL, DEFAULT 'active' | 状态（active/inactive） |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| user_id | INTEGER | FOREIGN KEY, NOT NULL | 所属用户ID |

**索引**：
- `user_id` 外键索引

**关联关系**：
- 多对一：`carbon_zones` → `users`
- 一对多：`carbon_zones` → `zone_measurements`

**坐标格式**：
```json
[
  [22.5828, 113.9686],
  [22.5829, 113.9687],
  ...
]
```

#### 3. zone_measurements（监测数据表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 主键，自增 |
| zone_id | INTEGER | FOREIGN KEY, NOT NULL | 监测区ID |
| ndvi | DECIMAL | NOT NULL | NDVI值（归一化植被指数，0-1） |
| carbon_absorption | DECIMAL | NOT NULL | 碳吸收量（吨/天） |
| timestamp | TIMESTAMP | NOT NULL, DEFAULT NOW() | 时间戳 |

**索引**：
- `zone_id` 外键索引
- `timestamp` 索引（用于时间序列查询）

**关联关系**：
- 多对一：`zone_measurements` → `carbon_zones`

#### 4. carbon_prices（价格表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 主键，自增 |
| price | DECIMAL | NOT NULL | 价格（元/吨） |
| timestamp | TIMESTAMP | NOT NULL, DEFAULT NOW() | 时间戳 |
| source | VARCHAR(100) | | 数据来源 |

**索引**：
- `timestamp` 索引（用于历史查询）

### 数据库关系图

```
┌──────────┐
│  users   │
│──────────│
│ id (PK)  │
│ username │
│ email    │
│ role     │
└────┬─────┘
     │ 1
     │
     │ *
┌────▼─────────┐
│carbon_zones  │
│──────────────│
│ id (PK)      │
│ name         │
│ coordinates  │
│ area         │
│ status       │
│ user_id (FK) │
└────┬─────────┘
     │ 1
     │
     │ *
┌────▼──────────────┐
│zone_measurements  │
│───────────────────│
│ id (PK)           │
│ zone_id (FK)      │
│ ndvi              │
│ carbon_absorption │
│ timestamp         │
└───────────────────┘

┌──────────────┐
│carbon_prices │
│──────────────│
│ id (PK)      │
│ price        │
│ timestamp    │
│ source       │
└──────────────┘
```

---

## API接口设计

### API规范

- **基础URL**：`http://localhost:8001/api`（开发环境）
- **认证方式**：JWT Bearer Token
- **请求格式**：JSON
- **响应格式**：JSON

### 接口列表

#### 认证接口 (`/api/auth`)

**POST /api/auth/register** - 用户注册
```json
Request:
{
  "username": "string",
  "email": "string",
  "password": "string"
}

Response:
{
  "id": 1,
  "username": "string",
  "email": "string",
  "role": "user",
  "created_at": "2024-01-01T00:00:00"
}
```

**POST /api/auth/login** - 用户登录
```json
Request:
{
  "username": "string",
  "password": "string"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### 监测区接口 (`/api/zones`)

**GET /api/zones/** - 获取监测区列表
- **认证**：必需
- **响应**：当前用户的所有监测区列表

**POST /api/zones/** - 创建监测区
```json
Request:
{
  "name": "string",
  "coordinates": [[22.5828, 113.9686], ...],
  "area": 1234.56
}
```

**GET /api/zones/{zone_id}** - 获取单个监测区
- **认证**：必需
- **权限**：只能访问自己的监测区

**PUT /api/zones/{zone_id}** - 更新监测区
```json
Request:
{
  "name": "string",
  "coordinates": [[...]],
  "area": 1234.56,
  "status": "active"
}
```

**DELETE /api/zones/{zone_id}** - 删除监测区
- **认证**：必需
- **级联删除**：会同时删除该监测区的所有监测数据

#### 监测数据接口 (`/api/measurements`)

**GET /api/measurements/zone/{zone_id}** - 获取监测数据列表
- **查询参数**：
  - `limit` - 返回数量限制（默认100）
  - `offset` - 偏移量
- **响应**：监测数据数组

**GET /api/measurements/zone/{zone_id}/chart** - 获取图表数据
- **响应**：格式化的时间序列数据，用于ECharts图表

**POST /api/measurements/** - 创建监测数据
```json
Request:
{
  "zone_id": 1,
  "ndvi": 0.75,
  "carbon_absorption": 12.5
}
```
- **权限**：管理员或自动生成服务

#### 价格接口 (`/api/prices`)

**GET /api/prices/current** - 获取当前价格
- **响应**：最新的价格记录

**GET /api/prices/history** - 获取价格历史
- **查询参数**：
  - `limit` - 返回数量限制（默认100）
- **响应**：价格历史数组

**POST /api/prices/generate-mock** - 生成模拟价格
- **权限**：仅管理员

---

## 核心功能模块

### 1. 用户认证系统

**功能特性**：
- JWT Token认证
- 密码复杂度验证（必须包含大小写字母和数字）
- 角色权限管理（admin/user）
- Token过期时间：24小时

**实现细节**：
- 密码使用 `pbkdf2_sha256` 算法加密存储
- Token通过 `python-jose` 生成和验证
- 前端通过 `localStorage` 持久化Token
- 路由守卫自动拦截未认证请求

### 2. 地图交互系统

**功能特性**：
- Leaflet地图集成
- 监测区创建（点击地图添加点，最多7个点）
- 监测区可视化（多边形标记）
- 监测区编辑（拖拽顶点修改边界）
- 监测区删除

**实现细节**：
- 使用Shapely进行多边形面积计算
- 坐标格式：`[latitude, longitude]`（WGS84坐标系）
- 初始地图位置：深圳大学粤海校区（22.5828°N, 113.9686°E）
- 地图缩放级别：16

### 3. 数据可视化系统

**功能特性**：
- NDVI历史趋势折线图
- 碳吸收量历史趋势折线图
- 实时价格展示

**实现细节**：
- 使用ECharts + Vue-ECharts进行图表渲染
- 数据格式化为时间序列格式
- 支持时间范围筛选

### 4. 自动数据生成系统

**功能特性**：
- 定时任务：每6小时自动生成监测数据
- 为所有活跃状态的监测区生成数据
- 生成符合逻辑的NDVI和碳吸收量数据

**实现细节**：
- 使用 `schedule` 库实现定时任务
- 在独立线程中运行，不阻塞主应用
- 使用Faker生成随机但合理的数据
- NDVI范围：0.3-0.9
- 碳吸收量根据NDVI计算（正相关关系）

---

## 开发工作流

### 后端开发

1. **环境设置**：
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **启动开发服务器**：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. **访问API文档**：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

4. **代码结构规范**：
- API路由放在 `app/api/` 目录
- 业务逻辑放在 `app/services/` 目录
- 数据库模型放在 `app/models/` 目录
- Schema定义放在 `app/schemas/` 目录

### 前端开发

1. **环境设置**：
```bash
cd frontend
npm install
```

2. **启动开发服务器**：
```bash
npm run dev
```

3. **访问前端应用**：
- 开发服务器: http://localhost:5173 (Vite默认端口)

4. **构建生产版本**：
```bash
npm run build
```

5. **代码规范**：
- 组件使用单文件组件（SFC）格式
- API调用统一放在 `src/api/` 目录
- 可复用组件放在 `src/components/` 目录
- 页面组件放在 `src/views/` 目录

### Docker开发

1. **启动所有服务**：
```bash
docker-compose up -d
```

2. **查看日志**：
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

3. **重启服务**：
```bash
docker-compose restart backend
docker-compose restart web
```

4. **停止服务**：
```bash
docker-compose down
```

---

## 部署架构

### 容器化部署

项目使用Docker Compose进行容器编排，包含三个服务：

1. **db** - PostgreSQL数据库容器
   - 端口映射：5433:5432
   - 数据卷：持久化存储
   - 健康检查：确保数据库就绪

2. **backend** - FastAPI后端容器
   - 端口映射：8001:8000
   - 代码卷：开发时实时同步代码
   - 依赖服务：db

3. **web** - Nginx Web容器
   - 端口映射：3000:80
   - 功能：
     - 静态文件服务（前端构建产物）
     - API反向代理（/api → backend:8000）
   - 依赖服务：backend

### 网络架构

```
Internet
   ↓
[Nginx:3000] ←── 用户访问入口
   ├── / → 前端静态文件
   └── /api/* → [Backend:8001] → [PostgreSQL:5433]
```

### 生产环境部署建议

1. **环境变量管理**：
   - 使用 `.env` 文件管理敏感配置
   - 生产环境修改 `SECRET_KEY`
   - 使用强密码的数据库连接

2. **安全配置**：
   - 启用HTTPS（通过Nginx配置SSL证书）
   - 配置CORS白名单
   - 设置合理的Token过期时间

3. **性能优化**：
   - 数据库连接池配置
   - 静态资源CDN加速
   - API响应缓存

4. **监控和日志**：
   - 应用日志集中管理
   - API响应时间监控
   - 错误异常告警

---

## 开发注意事项

### 后端开发

1. **数据库操作**：
   - 使用Session进行数据库操作，记得commit
   - 注意关联删除（cascade）
   - 使用事务处理复杂操作

2. **错误处理**：
   - 使用HTTPException抛出HTTP错误
   - 统一错误响应格式

3. **认证授权**：
   - 受保护的接口必须使用 `Depends(get_current_user)`
   - 管理员接口使用 `Depends(get_current_admin)`

### 前端开发

1. **API调用**：
   - 所有API调用统一使用 `src/api/` 中的封装函数
   - 错误处理统一在API层处理

2. **状态管理**：
   - 全局状态使用Pinia Store
   - 组件内部状态使用Vue的响应式数据

3. **路由导航**：
   - 使用 `router.push()` 进行编程式导航
   - 受保护路由会自动重定向

### 通用注意事项

1. **坐标系统**：
   - 统一使用WGS84坐标系（GPS坐标）
   - 格式：`[latitude, longitude]`

2. **时间格式**：
   - 后端返回ISO 8601格式
   - 前端使用Day.js处理时间格式化

3. **代码风格**：
   - Python遵循PEP 8规范
   - JavaScript使用ESLint和Prettier格式化

---

## 扩展开发指南

### 添加新的API端点

1. 在 `app/api/` 中创建或修改路由文件
2. 定义对应的Schema（如果需要）
3. 实现Service层业务逻辑
4. 在 `app/main.py` 中注册路由

### 添加新的数据库表

1. 在 `app/models/` 中定义模型
2. 在 `app/models/__init__.py` 中导出
3. 创建对应的Schema
4. 数据库表会在应用启动时自动创建

### 添加新的前端组件

1. 在 `src/components/` 中创建组件
2. 在需要的页面中引入和使用
3. 如需API调用，在 `src/api/` 中添加对应函数

### 添加新的定时任务

1. 在 `app/services/` 中创建任务函数
2. 在 `app/main.py` 的 `run_scheduler()` 函数中注册
3. 使用 `schedule` 库设置执行频率

---

## 总结

本文档详细介绍了CarbonCount项目的整体架构和代码结构。项目采用前后端分离的架构，后端使用FastAPI提供RESTful API，前端使用Vue3构建单页应用，通过Docker Compose实现容器化部署。

**关键设计理念**：
- **分层架构**：清晰的职责分离
- **组件化**：可复用的代码模块
- **容器化**：一致的开发和生产环境
- **API驱动**：前后端通过RESTful API通信

**后续开发建议**：
- 继续完善错误处理和日志系统
- 添加单元测试和集成测试
- 优化数据库查询性能
- 完善API文档和接口文档
- 添加更多数据可视化功能

---

**文档版本**：1.0.0  
**最后更新**：2024年  
**维护者**：开发团队
