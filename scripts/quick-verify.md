# 快速验证数据库数据

## 直接进入数据库容器

```powershell
docker-compose exec db psql -U carbonuser -d carboncount
```

然后执行以下 SQL 查询：

### 1. 查看数据统计
```sql
SELECT '监测区' as 类型, COUNT(*) as 数量 FROM carbon_zones
UNION ALL
SELECT '用户', COUNT(*) FROM users
UNION ALL
SELECT '监测数据', COUNT(*) FROM zone_measurements;
```

### 2. 查看最新监测区
```sql
SELECT id, name, status, area, created_at 
FROM carbon_zones 
ORDER BY created_at DESC 
LIMIT 5;
```

### 3. 查看监测区统计数据
```sql
SELECT 
    z.id,
    z.name,
    z.status,
    COUNT(m.id) as 数据点数,
    ROUND(COALESCE(SUM(m.carbon_absorption), 0), 3) as 总碳汇量,
    ROUND(COALESCE(AVG(m.ndvi), 0), 4) as 平均NDVI
FROM carbon_zones z
LEFT JOIN zone_measurements m ON z.id = m.zone_id
GROUP BY z.id, z.name, z.status
ORDER BY z.created_at DESC;
```

### 4. 查看最新监测数据
```sql
SELECT id, zone_id, ndvi, carbon_absorption, timestamp 
FROM zone_measurements 
ORDER BY timestamp DESC 
LIMIT 5;
```

### 5. 退出
```sql
\q
```

---

## 一行命令验证

```powershell
# 查看监测区数量
docker-compose exec -T db psql -U carbonuser -d carboncount -c "SELECT COUNT(*) as 监测区数量 FROM carbon_zones;"

# 查看最新监测区
docker-compose exec -T db psql -U carbonuser -d carboncount -c "SELECT id, name, status FROM carbon_zones ORDER BY created_at DESC LIMIT 3;"

# 查看统计数据
docker-compose exec -T db psql -U carbonuser -d carboncount -c "SELECT z.id, z.name, COUNT(m.id) as 数据点数 FROM carbon_zones z LEFT JOIN zone_measurements m ON z.id = m.zone_id GROUP BY z.id, z.name;"
```

---

## 验证步骤建议

1. **在前端创建一个监测区**
2. **立即运行验证命令**：
   ```powershell
   docker-compose exec -T db psql -U carbonuser -d carboncount -c "SELECT id, name, status, area, created_at FROM carbon_zones ORDER BY created_at DESC LIMIT 1;"
   ```
3. **检查返回的数据是否与前端输入一致**

4. **更新监测区状态后验证**：
   ```powershell
   docker-compose exec -T db psql -U carbonuser -d carboncount -c "SELECT id, name, status FROM carbon_zones WHERE id = <你的zone_id>;"
   ```

5. **删除监测区后验证**：
   ```powershell
   docker-compose exec -T db psql -U carbonuser -d carboncount -c "SELECT * FROM carbon_zones WHERE id = <你的zone_id>;"
   ```
   应该返回空结果
