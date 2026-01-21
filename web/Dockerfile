FROM node:18-alpine AS build

WORKDIR /app

# 安装依赖
COPY frontend/package*.json ./
RUN npm install

# 构建前端静态文件
COPY frontend/ ./
RUN npm run build

# 使用 Nginx 托管静态文件并反向代理 /api
FROM nginx:alpine

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
