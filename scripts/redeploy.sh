#!/bin/bash
# CarbonCount 重新部署脚本（服务器端使用）
# 用于重新部署 web、db、backend 三个服务

set -e  # 遇到错误立即退出

echo "=========================================="
echo "CarbonCount 重新部署脚本"
echo "=========================================="

# 获取项目根目录（脚本所在目录的父目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo ""
echo "当前目录: $(pwd)"
echo ""

# 检查是否存在 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: 未找到 .env 文件"
    echo "正在从 env.example 创建 .env..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ 已创建 .env 文件，请编辑并设置正确的配置值（特别是 POSTGRES_PASSWORD 和 SECRET_KEY）"
        echo "   编辑完成后，请重新运行此脚本"
        exit 1
    else
        echo "❌ 错误: 未找到 env.example 文件"
        exit 1
    fi
fi

# 检查 Docker 和 Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未找到 docker 命令"
    exit 1
fi

if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: 未找到 docker compose 命令"
    exit 1
fi

# 确定使用 docker compose 还是 docker-compose
if command -v docker compose &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "使用命令: $COMPOSE_CMD"
echo ""

# 询问是否拉取最新代码（如果使用 git）
if [ -d ".git" ]; then
    read -p "是否拉取最新代码? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📥 拉取最新代码..."
        git pull
        echo ""
    fi
fi

# 停止现有服务
echo "🛑 停止现有服务..."
$COMPOSE_CMD -f docker-compose.prod.yml down

# 清理旧的镜像（可选，询问用户）
read -p "是否清理未使用的镜像? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 清理未使用的镜像..."
    docker image prune -f
    echo ""
fi

# 重新构建并启动服务
echo "🔨 重新构建并启动服务..."
$COMPOSE_CMD -f docker-compose.prod.yml up -d --build

# 等待服务启动
echo ""
echo "⏳ 等待服务启动（10秒）..."
sleep 10

# 检查服务状态
echo ""
echo "📊 服务状态:"
$COMPOSE_CMD -f docker-compose.prod.yml ps

echo ""
echo "=========================================="
echo "✅ 重新部署完成！"
echo "=========================================="
echo ""
echo "查看日志:"
echo "  $COMPOSE_CMD -f docker-compose.prod.yml logs -f"
echo ""
echo "查看特定服务日志:"
echo "  $COMPOSE_CMD -f docker-compose.prod.yml logs -f web"
echo "  $COMPOSE_CMD -f docker-compose.prod.yml logs -f backend"
echo "  $COMPOSE_CMD -f docker-compose.prod.yml logs -f db"
echo ""
echo "停止服务:"
echo "  $COMPOSE_CMD -f docker-compose.prod.yml down"
echo ""
