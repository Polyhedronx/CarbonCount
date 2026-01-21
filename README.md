# 碳汇监测Web应用

基于FastAPI + Vue3/Vite + Docker + PostgreSQL开发的碳汇监测Web应用。

## 项目结构

```
CarbonCount_Fastapi/
├── backend/                    # FastAPI后端
│   ├── app/
│   │   ├── api/               # API路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic模型
│   │   └── services/          # 业务逻辑
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Vue3前端
│   ├── src/
│   │   ├── components/        # 组件
│   │   ├── views/            # 页面
│   │   ├── stores/           # 状态管理
│   │   ├── api/              # API调用
│   │   └── utils/            # 工具函数
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml          # Docker编排
├── docs/requirements.md        # 需求文档
└── README.md
```

## 技术栈

### 后端
- **FastAPI**: 高性能Web框架
- **SQLAlchemy**: ORM数据库操作
- **PostgreSQL**: 关系型数据库
- **JWT**: 用户认证
- **Pydantic**: 数据验证

### 前端
- **Vue 3**: 渐进式JavaScript框架
- **Vite**: 快速构建工具
- **Leaflet**: 地图库
- **Element Plus**: UI组件库
- **Pinia**: 状态管理
- **ECharts**: 图表库

### 部署
- **Docker**: 容器化
- **docker-compose**: 多容器编排

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
- 前端: http://localhost:3000
- 后端API文档: http://localhost:8000/docs

### 默认管理员账号
- 用户名: `admin`
- 密码: `Admin123`

## 功能特性

### 用户系统
- ✅ 用户注册/登录
- ✅ JWT认证
- ✅ 角色权限管理（管理员/普通用户）

### 地图功能
- ✅ Leaflet地图集成
- ✅ 深圳大学粤海校区初始位置
- ✅ 创建碳汇监测区（最多7个点）
- ✅ 区域编辑和管理

### 数据管理
- ✅ 碳汇监测区CRUD操作
- ✅ 实时碳汇价格展示
- ✅ 监测数据存储和查询

### 界面设计
- ✅ 响应式Dashboard布局
- ✅ 左侧控制面板
- ✅ 个人中心集成

## API接口

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册

### 监测区接口
- `GET /api/zones/` - 获取监测区列表
- `POST /api/zones/` - 创建监测区
- `GET /api/zones/{zone_id}` - 获取单个监测区
- `PUT /api/zones/{zone_id}` - 更新监测区
- `DELETE /api/zones/{zone_id}` - 删除监测区

### 监测数据接口
- `GET /api/measurements/zone/{zone_id}` - 获取区域监测数据
- `GET /api/measurements/zone/{zone_id}/chart` - 获取图表数据
- `POST /api/measurements/` - 创建监测数据

### 价格接口
- `GET /api/prices/current` - 获取当前价格
- `GET /api/prices/history` - 获取价格历史
- `POST /api/prices/generate-mock` - 生成模拟价格

## 开发指南

### 后端开发
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

### 数据库迁移
```bash
# 进入backend容器
docker-compose exec backend bash
# 数据库表会自动创建
```

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

## 待完成功能

- [ ] 监测数据自动生成服务
- [ ] NDVI和碳吸收量历史图表
- [ ] 区域数据导出功能
- [ ] 实时数据更新
- [ ] 高级地图功能（卫星影像等）

## 许可证

MIT License