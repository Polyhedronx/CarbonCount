# CarbonCount 远程服务器部署文档（IP + HTTP / Docker Compose 生产部署）

本文档面向 **远程 Linux 服务器**（仅 IP、先不配置 HTTPS），使用 **Docker Compose** 一键部署本项目的三类服务：

- `db`：PostgreSQL（数据持久化到 volume）
- `backend`：FastAPI（不对公网暴露端口，由 `web` 转发访问）
- `web`：Nginx（托管前端静态文件，并将 `/api` 反向代理到 `backend`）

> 开发环境仍可继续使用根目录的 `docker-compose.yml`（带热重载/源码挂载/端口暴露）。  
> 生产部署使用本文档对应的 `docker-compose.prod.yml`。

---

## 1. 部署前准备（服务器）

### 1.1 系统与权限
- 推荐：Ubuntu 22.04+/Debian 12+/CentOS 9+（任意支持 Docker 的发行版均可）
- 需要具备 sudo 权限的用户（建议不要使用 root 直接操作，但可以）

### 1.2 安装 Docker 与 Compose
按官方文档安装（不同系统命令略有差异）。安装完成后确认：

```bash
docker version
docker compose version
```

### 1.3 放行端口
本方案默认使用 **80**（可改为 3000/8080 等），你只需要对外开放一个 Web 端口：

- 入站：`80/tcp`（或你计划映射的端口）
- **不要**对公网开放数据库端口（生产 compose 默认不映射 Postgres 端口）

---

## 2. 获取代码（服务器）

选择一种方式：

### 方式 A：服务器直接拉取仓库
```bash
mkdir -p /opt/carboncount
cd /opt/carboncount
git clone <your-repo-url> .
```

### 方式 B：本地打包上传
将项目目录打包后上传到服务器解压到 `/opt/carboncount`（不展开赘述）。

---

## 3. 配置生产环境变量（必做）

项目后端会在启动时读取项目根目录的 `.env`（见 `backend/app/core/config.py` 的 `env_file = ".env"`）。

在服务器项目根目录执行：

```bash
cd /opt/carboncount
cp env.example .env
```

然后编辑 `.env`，至少修改以下两项：
- `POSTGRES_PASSWORD`：强密码
- `SECRET_KEY`：随机长字符串（建议 ≥ 32 字符）

> 注意：仓库已在 `.gitignore` 忽略 `.env`，请不要把真实 `.env` 提交到 git。

---

## 4. 启动生产服务

### 4.1 首次启动（构建 + 后台运行）
```bash
cd /opt/carboncount
docker compose -f docker-compose.prod.yml up -d --build
```

### 4.2 查看运行状态
```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f --tail=200
```

### 4.3 访问验证
假设服务器 IP 为 `1.2.3.4` 且 `WEB_PORT=80`：

- 前端入口：`http://1.2.3.4/`
- 后端文档（通过 web 转发）：`http://1.2.3.4/api/docs`
  - 如果你的 FastAPI 文档路径不是 `/api/docs`，可以改用：`http://1.2.3.4/api` 下的任意接口验证（例如登录/获取价格）

---

## 5. 更新发布（常用）

### 5.1 拉取代码并重建
```bash
cd /opt/carboncount
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

说明：
- 后端依赖或代码变更：需要 `--build`
- 前端变更（Vue build 输出变化）：需要 `--build`（因为 web 镜像会重新构建前端静态文件）

### 5.2 回滚（建议做法）
最简单的回滚方式是回退 git 版本再重建：

```bash
cd /opt/carboncount
git log --oneline -n 10
git checkout <commit-sha>
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 6. 数据持久化、备份与恢复（PostgreSQL）

### 6.1 数据持久化位置
生产 compose 使用 `postgres_data` volume 持久化数据库：
- 容器内：`/var/lib/postgresql/data`
- 宿主机具体路径由 Docker 管理（不同系统不同）

### 6.2 备份（推荐定期执行）
在服务器执行：

```bash
cd /opt/carboncount
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup_$(date +%F).sql
```

### 6.3 恢复（从 .sql 导入）
```bash
cd /opt/carboncount
cat backup_YYYY-MM-DD.sql | docker compose -f docker-compose.prod.yml exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

> `backend/init.sql` 只会在数据库 volume 首次初始化时执行；如果 `postgres_data` 已存在，后续不会重复执行。

---

## 7. 日志与排障

### 7.1 看日志
```bash
docker compose -f docker-compose.prod.yml logs -f --tail=200 web
docker compose -f docker-compose.prod.yml logs -f --tail=200 backend
docker compose -f docker-compose.prod.yml logs -f --tail=200 db
```

### 7.2 常见问题

#### (1) 访问前端正常，但 `/api` 502
- 先看 `backend` 是否健康/是否启动成功
- 看 `web` 容器日志是否有 upstream 错误
- 确认 `backend` 在容器内监听 `0.0.0.0:8000`（生产 compose 已设置）

#### (2) 数据库连接失败
- 确认 `.env` 中 `DATABASE_URL` 指向 `db:5432`
- 确认 `.env` 中 `POSTGRES_PASSWORD` 与 `DATABASE_URL` 中密码一致
- 查看 `db` 日志是否因权限/磁盘/volume 损坏启动失败

#### (3) 需要临时进入数据库查看数据
```bash
docker compose -f docker-compose.prod.yml exec db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

---

## 8. 最低限度安全建议（无 HTTPS 前提）

- **不要**对公网暴露 Postgres 端口（生产 compose 默认不映射）
- 修改所有默认密钥/密码：`.env` 里的 `POSTGRES_PASSWORD`、`SECRET_KEY`
- 服务器防火墙只开放一个 Web 端口（如 80/3000/8080）
- 后续若要支持域名与 HTTPS：建议在服务器前面加宿主机 Nginx/Caddy 或使用 Traefik，并启用 Let’s Encrypt 自动证书