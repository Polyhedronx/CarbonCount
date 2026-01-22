# 数据库验证脚本
# 用途：快速验证前端数据是否正确存入数据库

Write-Host "`n=== 数据库验证脚本 ===" -ForegroundColor Green
Write-Host "正在连接数据库..." -ForegroundColor Yellow

# 检查容器是否运行
$dbStatus = docker-compose ps db --format json | ConvertFrom-Json
if ($dbStatus.Status -notlike "*Up*") {
    Write-Host "错误：数据库容器未运行！" -ForegroundColor Red
    Write-Host "请先运行: docker-compose up -d db" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n1. 查看数据统计信息" -ForegroundColor Cyan
$sql1 = @"
SELECT 
    '监测区数量' as 类型,
    COUNT(*)::text as 数量
FROM carbon_zones
UNION ALL
SELECT 
    '用户数量' as 类型,
    COUNT(*)::text as 数量
FROM users
UNION ALL
SELECT 
    '监测数据数量' as 类型,
    COUNT(*)::text as 数量
FROM zone_measurements;
"@
docker-compose exec -T db psql -U carbonuser -d carboncount -c $sql1

Write-Host "`n2. 查看最新的监测区（前5个）" -ForegroundColor Cyan
$sql2 = @"
SELECT 
    id as ID,
    name as 名称,
    status as 状态,
    ROUND(area::numeric, 2) as 面积平方米,
    created_at as 创建时间
FROM carbon_zones 
ORDER BY created_at DESC 
LIMIT 5;
"@
docker-compose exec -T db psql -U carbonuser -d carboncount -c $sql2

Write-Host "`n3. 查看用户列表" -ForegroundColor Cyan
$sql3 = @"
SELECT 
    id as ID,
    username as 用户名,
    email as 邮箱,
    role as 角色,
    created_at as 创建时间
FROM users 
ORDER BY created_at DESC;
"@
docker-compose exec -T db psql -U carbonuser -d carboncount -c $sql3

Write-Host "`n4. 查看监测区及其统计数据" -ForegroundColor Cyan
$sql4 = @"
SELECT 
    z.id as 监测区ID,
    z.name as 名称,
    z.status as 状态,
    COUNT(m.id) as 数据点数,
    ROUND(COALESCE(SUM(m.carbon_absorption), 0)::numeric, 3) as 总碳汇量,
    ROUND(COALESCE(AVG(m.ndvi), 0)::numeric, 4) as 平均NDVI
FROM carbon_zones z
LEFT JOIN zone_measurements m ON z.id = m.zone_id
GROUP BY z.id, z.name, z.status
ORDER BY z.created_at DESC;
"@
docker-compose exec -T db psql -U carbonuser -d carboncount -c $sql4

Write-Host "`n5. 查看最新的监测数据（前5条）" -ForegroundColor Cyan
$sql5 = @"
SELECT 
    id as ID,
    zone_id as 监测区ID,
    ROUND(ndvi::numeric, 4) as NDVI,
    ROUND(carbon_absorption::numeric, 6) as 碳吸收量,
    timestamp as 时间戳
FROM zone_measurements 
ORDER BY timestamp DESC 
LIMIT 5;
"@
docker-compose exec -T db psql -U carbonuser -d carboncount -c $sql5

Write-Host "`n=== 验证完成 ===" -ForegroundColor Green
Write-Host "`n提示：" -ForegroundColor Yellow
Write-Host "  - 要查看详细信息，运行: docker-compose exec db psql -U carbonuser -d carboncount" -ForegroundColor Gray
Write-Host "  - 要查看特定监测区，运行上面的命令后执行: SELECT * FROM carbon_zones WHERE id = <zone_id>;" -ForegroundColor Gray
Write-Host "  - 要查看完整验证指南，请查看: docs/database_verification.md" -ForegroundColor Gray
