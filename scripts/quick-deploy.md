# 快速重新部署指南

## 服务器端重新部署（Linux）

### 方法一：使用部署脚本（推荐）

```bash
cd /opt/carboncount  # 或你的项目目录
chmod +x scripts/redeploy.sh
./scripts/redeploy.sh
```

脚本会引导你完成：
- ✅ 检查环境配置
- ✅ 拉取最新代码（可选）
- ✅ 停止现有服务
- ✅ 清理旧镜像（可选）
- ✅ 重新构建并启动服务

### 方法二：手动命令

```bash
cd /opt/carboncount

# 1. 拉取最新代码
git pull

# 2. 停止现有服务
docker compose -f docker-compose.prod.yml down

# 3. 重新构建并启动
docker compose -f docker-compose.prod.yml up -d --build

# 4. 查看状态
docker compose -f docker-compose.prod.yml ps

# 5. 查看日志（如有问题）
docker compose -f docker-compose.prod.yml logs -f
```

## 常用命令

### 查看服务状态
```bash
docker compose -f docker-compose.prod.yml ps
```

### 查看日志
```bash
# 所有服务
docker compose -f docker-compose.prod.yml logs -f

# 特定服务
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f db
```

### 重启单个服务
```bash
docker compose -f docker-compose.prod.yml restart web
docker compose -f docker-compose.prod.yml restart backend
docker compose -f docker-compose.prod.yml restart db
```

### 停止所有服务
```bash
docker compose -f docker-compose.prod.yml down
```

### 停止并清理（包括数据卷，谨慎使用）
```bash
docker compose -f docker-compose.prod.yml down -v
```

## 仅更新代码不重建镜像

如果只是修改了代码，但不想重新构建镜像（使用已构建的镜像）：

```bash
docker compose -f docker-compose.prod.yml up -d
```

**注意**：生产环境通常不挂载源码，所以代码变更必须重新构建镜像。

## 仅重建特定服务

```bash
# 只重建 backend
docker compose -f docker-compose.prod.yml up -d --build backend

# 只重建 web
docker compose -f docker-compose.prod.yml up -d --build web
```

## 验证部署

部署完成后，访问：
- 前端：`http://你的服务器IP/`
- API文档：`http://你的服务器IP/api/docs`

## 故障排查

### 服务无法启动
1. 检查日志：`docker compose -f docker-compose.prod.yml logs`
2. 检查 .env 配置是否正确
3. 检查端口是否被占用
4. 检查磁盘空间：`df -h`

### 数据库连接失败
1. 确认 .env 中 `DATABASE_URL` 正确
2. 确认数据库服务已启动：`docker compose -f docker-compose.prod.yml ps db`
3. 查看数据库日志：`docker compose -f docker-compose.prod.yml logs db`

### API 502 错误
1. 确认 backend 服务已启动
2. 查看 backend 日志：`docker compose -f docker-compose.prod.yml logs backend`
3. 检查 web 容器是否能访问 backend：`docker compose -f docker-compose.prod.yml exec web ping backend`
