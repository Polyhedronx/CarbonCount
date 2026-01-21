-- 初始化数据库和管理员用户
-- 注意：密码是 'Admin123' 的bcrypt哈希值

INSERT INTO users (username, email, password_hash, role, created_at, is_active)
VALUES (
    'admin',
    'admin@carboncount.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewfBPj6fMJyHnUeK', -- Admin123
    'admin',
    CURRENT_TIMESTAMP,
    true
) ON CONFLICT (username) DO NOTHING;