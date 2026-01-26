-- 初始化数据库和管理员用户
-- 注意：密码是 'Admin123' 的bcrypt哈希值
-- 注意：表由 FastAPI 应用通过 SQLAlchemy 创建，此脚本在表创建后执行

-- 使用 DO 块检查表是否存在，如果存在则插入管理员用户
DO $$
BEGIN
    -- 检查 users 表是否存在
    IF EXISTS (SELECT FROM information_schema.tables 
               WHERE table_schema = 'public' 
               AND table_name = 'users') THEN
        -- 表存在，尝试插入管理员用户
        INSERT INTO users (username, email, password_hash, role, created_at, is_active)
        VALUES (
            'admin',
            'admin@carboncount.com',
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewfBPj6fMJyHnUeK', -- Admin123
            'admin',
            CURRENT_TIMESTAMP,
            true
        ) ON CONFLICT (username) DO NOTHING;
    ELSE
        -- 表不存在，记录信息（表将由 FastAPI 应用创建）
        RAISE NOTICE 'users 表不存在，将由 FastAPI 应用创建。管理员用户可通过应用启动后手动创建。';
    END IF;
END $$;
