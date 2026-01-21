# 项目部署指南

本文档旨在指导 CarbonCount 项目的部署流程。项目包含后端 API、前端静态资源及数据库服务。

**架构说明：**
*   **后端**：FastAPI，监听端口 `8000`（容器内），对外映射为 `8001`。
*   **前端**：构建为静态文件，通过 Nginx 托管。
*   **反向代理**：推荐使用 Nginx 将前端请求中的 `/api` 路径（所有以 `/api` 开头的请求）转发至后端服务，解决跨域问题。
*   **数据库**：PostgreSQL。

---

## 一、全栈一键部署 (Docker Compose)

适用于本地开发、测试环境或基于 Docker 的生产环境部署。该模式下包含数据库、后端及内含 Nginx 的 Web 服务容器。

### 1. 启动服务
进入项目根目录并启动所有容器：

```powershell
# 进入项目目录
cd CarbonCount_Fastapi

# 后台启动所有服务 (db, backend, web)
docker-compose up -d
```

### 2. 访问服务
服务启动成功后，可通过以下地址访问：

*   **前端页面 (Web)**：`http://localhost:3000`
    *   *说明：由 Nginx 容器提供服务，已配置好静态文件托管及 API 反代。*
*   **后端接口文档 (OpenAPI)**：`http://localhost:8001/docs`

### 3. 代码更新与维护
*   **修改后端代码后**：
    ```powershell
    docker-compose restart backend
    ```
*   **修改前端代码或 Nginx 配置后**：
    需要重新构建 Web 镜像：
    ```powershell
    docker-compose up -d --build web
    ```

---

## 二、独立部署后端 API

适用于只需要后端接口服务，或者正在进行后端调试的场景。

### 1. 启动数据库与后端
```powershell
cd CarbonCount_Fastapi
docker-compose up -d db backend
```

### 2. 服务地址
*   **API 接口**：`http://localhost:8001/api/...`
*   **接口文档**：`http://localhost:8001/docs`

### 3. 配置说明
如需修改数据库连接地址或密钥，有以下几种方式：

*   **Docker 部署（推荐）**：直接编辑 `docker-compose.yml` 中 `backend` 服务的 `environment` 部分，修改完成后重启 backend 容器生效：
    ```powershell
    docker-compose restart backend
    ```

*   **本地运行（非 Docker）**：
    *   在项目根目录创建修改 `.env` 文件（`config.py` 会在当前工作目录查找 `.env`）
    *   或直接修改 `backend/app/core/config.py` 中的默认值

---

## 三、生产环境手动部署 (Nginx + 静态文件)

生产环境推荐使用宿主机 Nginx 直接托管构建后的前端静态文件，并通过反向代理连接后端。

### 1. 构建前端静态资源
在本地或构建服务器上执行构建命令：

```powershell
cd CarbonCount_Fastapi/frontend
npm install
npm run build
```
构建完成后，生成的静态文件位于 `frontend/dist` 目录。

### 2. 配置 Nginx
将 `frontend/dist` 目录下的所有文件上传至服务器目录（例如：`/var/www/carboncount`）。

编辑 Nginx 配置文件（示例）：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 静态文件根目录
    root /var/www/carboncount;
    index index.html;

    # 前端路由支持（防止刷新 404）
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 反向代理配置：将 /api 转发至后端容器或服务
    # 注意：使用 /api 而不是 /api/ 以匹配所有 /api 开头的路径
    location /api {
        # 假设后端运行在本地 8001 端口
        # 注意：proxy_pass 后不带路径，以保留完整的 /api 前缀
        proxy_pass http://127.0.0.1:8001;
        
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**关键点**：前端代码中无需配置绝对路径 URL，统一请求同域的 `/api` 路径，由 Nginx 负责转发。

---

## 四、配置参数速查

### 1. 端口映射
| 服务 | 容器内部端口 | 对外映射端口 | 说明 |
| :--- | :--- | :--- | :--- |
| **Web (Nginx)** | 80 | 3000 | 前端访问入口 |
| **Backend** | 8000 | 8001 | 后端 API 入口 |
| **Database** | 5432 | 5433 | 数据库连接端口 |

### 2. 关键环境变量

**Docker 部署**：在 `docker-compose.yml` 中 `backend` 服务的 `environment` 部分配置。

**本地运行（非 Docker）**：在项目根目录创建 `.env` 文件配置。

关键变量：
*   `DATABASE_URL`：PostgreSQL 连接字符串（Docker 模式下默认指向服务名 `db`）。
*   `SECRET_KEY`：用于 JWT 签名和加密的密钥，生产环境请务必修改。

**注意**：前端代码使用硬编码的相对路径 `/api`，通过 Nginx 反向代理或 Vite 开发代理转发到后端，无需配置额外的环境变量。

---

## 五、常见问题排查

**1. 前端请求无法到达后端 (404 或 Network Error)**
*   检查 Nginx 配置中的 `location /api` 是否正确（注意不是 `/api/`）。
*   确认 `proxy_pass` 后不带路径（如 `http://127.0.0.1:8001` 而不是 `http://127.0.0.1:8001/`），以保留完整的 `/api` 前缀。
*   确认前端代码中的请求路径是否为相对路径（如 `/api/login`），而非硬编码的绝对路径。
*   确保后端容器已启动并映射到 Nginx 配置的 `proxy_pass` 端口（如 8001）。

**2. 管理员账号登录失败**
*   当前密码加密算法使用 `pbkdf2_sha256`。
*   如需创建管理员，请先通过注册接口创建一个普通用户，然后直接连接数据库将该用户的 `role` 字段更新为 `admin`。

**3. 代码修改后不生效**
*   如果是 Docker 部署，修改前端代码后必须执行 `docker-compose up -d --build web` 重建镜像。
*   修改后端代码后，建议执行 `docker-compose restart backend`。