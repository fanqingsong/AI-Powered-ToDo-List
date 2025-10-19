-- 数据库迁移脚本：添加用户角色字段
-- 执行此脚本前请备份数据库

-- 添加角色字段到users表
ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL;

-- 创建角色枚举类型（PostgreSQL）
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
        CREATE TYPE userrole AS ENUM ('user', 'admin');
    END IF;
END $$;

-- 更新role字段为枚举类型
ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole;

-- 为现有用户设置默认角色
UPDATE users SET role = 'user' WHERE role IS NULL;

-- 创建管理员用户（如果不存在）
INSERT INTO users (username, email, password_hash, display_name, role, is_active, created_at, updated_at)
SELECT 'admin', 'admin@example.com', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', '系统管理员', 'admin', true, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- 显示更新结果
SELECT 
    role,
    COUNT(*) as user_count
FROM users 
GROUP BY role
ORDER BY role;
