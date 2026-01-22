# 数据库验证指南

本文档介绍如何验证前端数据是否正确存入数据库。

## 数据库连接信息

- **数据库类型**: PostgreSQL
- **数据库名**: `carboncount`
- **用户名**: `carbonuser`
- **密码**: `carbonpass123`
- **容器内端口**: `5432`
- **外部端口**: `5433` (映射到本地)

---

## 方法一：通过 Docker 进入数据库容器（推荐）

### 1. 进入数据库容器

```powershell
# Windows PowerShell
docker-compose exec db psql -U carbonuser -d carboncount
```

### 2. 查看所有表

```sql
\dt
```

### 3. 查看监测区数据

```sql
-- 查看所有监测区
SELECT id, name, status, area, created_at, user_id 
FROM carbon_zones 
ORDER BY created_at DESC;

-- 查看监测区详细信息（包括坐标）
SELECT 
    id, 
    name, 
    status, 
    area, 
    coordinates,
    created_at,
    user_id
FROM carbon_zones 
ORDER BY created_at DESC;
```

### 4. 查看用户数据

```sql
-- 查看所有用户
SELECT id, username, email, role, created_at 
FROM users 
ORDER BY created_at DESC;
```

### 5. 查看监测数据

```sql
-- 查看监测数据（最近10条）
SELECT 
    id, 
    zone_id, 
    ndvi, 
    carbon_absorption, 
    timestamp 
FROM zone_measurements 
ORDER BY timestamp DESC 
LIMIT 10;

-- 查看特定监测区的数据
SELECT 
    id, 
    zone_id, 
    ndvi, 
    carbon_absorption, 
    timestamp 
FROM zone_measurements 
WHERE zone_id = 1  -- 替换为实际的zone_id
ORDER BY timestamp DESC;
```

### 6. 查看统计数据

```sql
-- 查看每个监测区的统计数据
SELECT 
    z.id,
    z.name,
    z.status,
    COUNT(m.id) as measurements_count,
    COALESCE(SUM(m.carbon_absorption), 0) as total_carbon_absorption,
    COALESCE(AVG(m.ndvi), 0) as average_ndvi
FROM carbon_zones z
LEFT JOIN zone_measurements m ON z.id = m.zone_id
GROUP BY z.id, z.name, z.status
ORDER BY z.created_at DESC;
```

### 7. 验证级联删除

```sql
-- 查看监测区及其关联的测量数据数量
SELECT 
    z.id,
    z.name,
    COUNT(m.id) as measurement_count
FROM carbon_zones z
LEFT JOIN zone_measurements m ON z.id = m.zone_id
GROUP BY z.id, z.name;
```

### 8. 退出 psql

```sql
\q
```

---

## 方法二：使用本地 psql 客户端连接

如果本地安装了 PostgreSQL 客户端：

```powershell
psql -h localhost -p 5433 -U carbonuser -d carboncount
```

然后输入密码：`carbonpass123`

---

## 方法三：通过后端 API 验证

### 1. 获取监测区列表

```powershell
# 首先需要登录获取 token
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/login" `
    -Method POST `
    -ContentType "application/x-www-form-urlencoded" `
    -Body "username=your_username&password=your_password"

$token = $loginResponse.access_token

# 获取监测区列表
$headers = @{
    "Authorization" = "Bearer $token"
}
Invoke-RestMethod -Uri "http://localhost:8001/api/zones/" `
    -Method GET `
    -Headers $headers | ConvertTo-Json -Depth 10
```

### 2. 查看 API 文档

访问：http://localhost:8001/docs

在 Swagger UI 中可以：
- 测试所有 API 接口
- 查看请求/响应格式
- 验证数据是否正确

---

## 方法四：查看 Docker 日志

### 查看后端日志（可以看到数据库操作）

```powershell
docker-compose logs -f backend
```

### 查看数据库日志

```powershell
docker-compose logs -f db
```

---

## 方法五：使用数据库管理工具

### 使用 DBeaver、pgAdmin 或其他工具连接

**连接信息**：
- **Host**: `localhost`
- **Port**: `5433`
- **Database**: `carboncount`
- **Username**: `carbonuser`
- **Password**: `carbonpass123`

---

## 快速验证脚本

创建一个 PowerShell 脚本来快速验证：

```powershell
# verify-database.ps1
Write-Host "=== 数据库验证脚本 ===" -ForegroundColor Green

# 进入数据库容器并执行查询
docker-compose exec -T db psql -U carbonuser -d carboncount <<EOF
SELECT 
    '监测区数量' as type,
    COUNT(*)::text as count
FROM carbon_zones
UNION ALL
SELECT 
    '用户数量' as type,
    COUNT(*)::text as count
FROM users
UNION ALL
SELECT 
    '监测数据数量' as type,
    COUNT(*)::text as count
FROM zone_measurements;
EOF
```

---

## 常见验证场景

### 场景1：验证创建监测区是否成功

```sql
-- 1. 查看最新创建的监测区
SELECT * FROM carbon_zones ORDER BY created_at DESC LIMIT 1;

-- 2. 验证坐标是否正确存储
SELECT id, name, coordinates FROM carbon_zones WHERE id = <zone_id>;
```

### 场景2：验证更新操作

```sql
-- 查看监测区状态
SELECT id, name, status FROM carbon_zones WHERE id = <zone_id>;

-- 查看监测区名称
SELECT id, name FROM carbon_zones WHERE id = <zone_id>;
```

### 场景3：验证删除操作

```sql
-- 1. 确认监测区已删除
SELECT * FROM carbon_zones WHERE id = <zone_id>;
-- 应该返回空结果

-- 2. 确认关联的测量数据也被删除（级联删除）
SELECT * FROM zone_measurements WHERE zone_id = <zone_id>;
-- 应该返回空结果
```

### 场景4：验证统计数据

```sql
-- 查看监测区的统计数据（应该与前端显示一致）
SELECT 
    z.id,
    z.name,
    COUNT(m.id) as measurements_count,
    COALESCE(SUM(m.carbon_absorption), 0) as total_carbon_absorption,
    COALESCE(AVG(m.ndvi), 0) as current_ndvi
FROM carbon_zones z
LEFT JOIN zone_measurements m ON z.id = m.zone_id
WHERE z.id = <zone_id>
GROUP BY z.id, z.name;
```

---

## 表结构参考

### carbon_zones 表

```sql
\d carbon_zones
```

主要字段：
- `id`: 主键
- `name`: 监测区名称
- `coordinates`: JSON格式的坐标数组
- `area`: 面积（平方米）
- `status`: 状态（active/inactive）
- `created_at`: 创建时间
- `user_id`: 用户ID

### zone_measurements 表

```sql
\d zone_measurements
```

主要字段：
- `id`: 主键
- `zone_id`: 监测区ID（外键）
- `ndvi`: NDVI值
- `carbon_absorption`: 碳吸收量
- `timestamp`: 时间戳

### users 表

```sql
\d users
```

主要字段：
- `id`: 主键
- `username`: 用户名
- `email`: 邮箱
- `hashed_password`: 加密密码
- `role`: 角色（user/admin）
- `created_at`: 创建时间

---

## 故障排查

### 问题1：无法连接数据库

```powershell
# 检查容器是否运行
docker-compose ps

# 检查数据库健康状态
docker-compose exec db pg_isready -U carbonuser -d carboncount
```

### 问题2：数据未保存

1. 检查后端日志：`docker-compose logs backend`
2. 检查数据库事务是否提交
3. 验证 API 响应是否成功

### 问题3：级联删除未生效

```sql
-- 检查外键约束
SELECT 
    conname as constraint_name,
    conrelid::regclass as table_name,
    confrelid::regclass as referenced_table
FROM pg_constraint
WHERE contype = 'f' 
AND confrelid = 'carbon_zones'::regclass;
```

---

## 提示

- 所有 SQL 查询都可以在 `docker-compose exec db psql` 中执行
- 使用 `\x` 可以切换扩展显示模式（更适合查看宽表）
- 使用 `\timing` 可以显示查询执行时间
- 使用 `\copy` 可以导出数据到 CSV
