# CarbonCount 重新部署脚本（Windows PowerShell，用于本地测试）
# 服务器端请使用 redeploy.sh

param(
    [switch]$SkipPull,
    [switch]$CleanImages,
    [switch]$NoBuild
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "CarbonCount 重新部署脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 获取项目根目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot

Write-Host "当前目录: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# 检查是否存在 .env 文件
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  警告: 未找到 .env 文件" -ForegroundColor Yellow
    Write-Host "正在从 env.example 创建 .env..."
    if (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
        Write-Host "✅ 已创建 .env 文件，请编辑并设置正确的配置值（特别是 POSTGRES_PASSWORD 和 SECRET_KEY）" -ForegroundColor Green
        Write-Host "   编辑完成后，请重新运行此脚本"
        exit 1
    } else {
        Write-Host "❌ 错误: 未找到 env.example 文件" -ForegroundColor Red
        exit 1
    }
}

# 检查 Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 错误: 未找到 docker 命令" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue) -and 
    -not (docker compose version 2>$null)) {
    Write-Host "❌ 错误: 未找到 docker compose 命令" -ForegroundColor Red
    exit 1
}

# 确定使用 docker compose 还是 docker-compose
$ComposeCmd = "docker-compose"
if (docker compose version 2>$null) {
    $ComposeCmd = "docker compose"
}

Write-Host "使用命令: $ComposeCmd" -ForegroundColor Gray
Write-Host ""

# 询问是否拉取最新代码（如果使用 git）
if (-not $SkipPull -and (Test-Path ".git")) {
    $pull = Read-Host "是否拉取最新代码? (y/n)"
    if ($pull -eq "y" -or $pull -eq "Y") {
        Write-Host "📥 拉取最新代码..." -ForegroundColor Cyan
        git pull
        Write-Host ""
    }
}

# 停止现有服务
Write-Host "🛑 停止现有服务..." -ForegroundColor Yellow
& $ComposeCmd -f docker-compose.prod.yml down

# 清理旧的镜像（可选）
if ($CleanImages) {
    Write-Host "🧹 清理未使用的镜像..." -ForegroundColor Cyan
    docker image prune -f
    Write-Host ""
} else {
    $clean = Read-Host "是否清理未使用的镜像? (y/n)"
    if ($clean -eq "y" -or $clean -eq "Y") {
        Write-Host "🧹 清理未使用的镜像..." -ForegroundColor Cyan
        docker image prune -f
        Write-Host ""
    }
}

# 重新构建并启动服务
if ($NoBuild) {
    Write-Host "🚀 启动服务（不重新构建）..." -ForegroundColor Cyan
    & $ComposeCmd -f docker-compose.prod.yml up -d
} else {
    Write-Host "🔨 重新构建并启动服务..." -ForegroundColor Cyan
    & $ComposeCmd -f docker-compose.prod.yml up -d --build
}

# 等待服务启动
Write-Host ""
Write-Host "⏳ 等待服务启动（10秒）..." -ForegroundColor Gray
Start-Sleep -Seconds 10

# 检查服务状态
Write-Host ""
Write-Host "📊 服务状态:" -ForegroundColor Cyan
& $ComposeCmd -f docker-compose.prod.yml ps

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ 重新部署完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "查看日志:" -ForegroundColor Gray
Write-Host "  $ComposeCmd -f docker-compose.prod.yml logs -f" -ForegroundColor White
Write-Host ""
Write-Host "查看特定服务日志:" -ForegroundColor Gray
Write-Host "  $ComposeCmd -f docker-compose.prod.yml logs -f web" -ForegroundColor White
Write-Host "  $ComposeCmd -f docker-compose.prod.yml logs -f backend" -ForegroundColor White
Write-Host "  $ComposeCmd -f docker-compose.prod.yml logs -f db" -ForegroundColor White
Write-Host ""
Write-Host "停止服务:" -ForegroundColor Gray
Write-Host "  $ComposeCmd -f docker-compose.prod.yml down" -ForegroundColor White
Write-Host ""
