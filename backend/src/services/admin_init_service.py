import asyncio
import hashlib
import os
from typing import Optional
from sqlalchemy import select, text
from ..database import get_db_session
from ..models.database_models import UserDB, UserRole
from ..models.auth import UserCreate, UserRole as AuthUserRole


class AdminInitializationService:
    """管理员账户初始化服务"""
    
    def __init__(self):
        # 从环境变量读取配置，如果没有则使用默认值
        self.admin_username = os.getenv("ADMIN_USERNAME", "admin")
        self.admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        self.admin_password = os.getenv("ADMIN_PASSWORD", "admin")
        self.admin_display_name = os.getenv("ADMIN_DISPLAY_NAME", "系统管理员")
    
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希"""
        # 使用简单的SHA256哈希（与AuthService保持一致）
        return hashlib.sha256(password.encode()).hexdigest()
    
    async def check_admin_exists(self) -> bool:
        """检查管理员账户是否存在"""
        async with get_db_session() as session:
            # 检查是否有任何管理员用户
            query = select(UserDB).where(UserDB.role == UserRole.ADMIN)
            result = await session.execute(query)
            admin_user = result.scalar_one_or_none()
            return admin_user is not None
    
    async def create_admin_user(self) -> bool:
        """创建管理员账户"""
        async with get_db_session() as session:
            try:
                # 检查用户名和邮箱是否已存在
                existing_query = select(UserDB).where(
                    (UserDB.username == self.admin_username) | 
                    (UserDB.email == self.admin_email)
                )
                existing_result = await session.execute(existing_query)
                existing_user = existing_result.scalar_one_or_none()
                
                if existing_user:
                    # 如果用户存在但角色不是管理员，更新为管理员
                    if existing_user.role != UserRole.ADMIN:
                        existing_user.role = UserRole.ADMIN
                        existing_user.display_name = self.admin_display_name
                        await session.commit()
                        print(f"✅ 用户 {self.admin_username} 已更新为管理员角色")
                        return True
                    else:
                        print(f"ℹ️ 管理员用户 {self.admin_username} 已存在")
                        return True
                
                # 创建新的管理员用户
                admin_user = UserDB(
                    username=self.admin_username,
                    email=self.admin_email,
                    password_hash=self.get_password_hash(self.admin_password),
                    display_name=self.admin_display_name,
                    role=UserRole.ADMIN,
                    is_active=True
                )
                
                session.add(admin_user)
                await session.commit()
                
                print(f"✅ 管理员账户创建成功: {self.admin_username}")
                print(f"   用户名: {self.admin_username}")
                print(f"   密码: {self.admin_password}")
                print(f"   邮箱: {self.admin_email}")
                return True
                
            except Exception as e:
                print(f"❌ 创建管理员账户失败: {e}")
                await session.rollback()
                return False
    
    async def ensure_admin_exists(self) -> bool:
        """确保管理员账户存在"""
        try:
            # 首先检查管理员是否存在
            admin_exists = await self.check_admin_exists()
            
            if admin_exists:
                print("✅ 管理员账户已存在")
                return True
            
            # 如果不存在，创建管理员账户
            print("⚠️ 未找到管理员账户，正在创建...")
            return await self.create_admin_user()
            
        except Exception as e:
            print(f"❌ 检查/创建管理员账户时出错: {e}")
            return False
    
    async def initialize_database_schema(self) -> bool:
        """初始化数据库架构（如果需要）"""
        async with get_db_session() as session:
            try:
                # 检查role字段是否存在
                result = await session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'role'
                """))
                
                role_column_exists = result.fetchone() is not None
                
                if not role_column_exists:
                    print("⚠️ 检测到users表缺少role字段，正在添加...")
                    
                    # 添加role字段
                    await session.execute(text("""
                        ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL
                    """))
                    
                    # 创建角色枚举类型（如果不存在）
                    await session.execute(text("""
                        DO $$ 
                        BEGIN
                            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
                                CREATE TYPE userrole AS ENUM ('user', 'admin');
                            END IF;
                        END $$;
                    """))
                    
                    # 更新role字段为枚举类型
                    await session.execute(text("""
                        ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole
                    """))
                    
                    # 为现有用户设置默认角色
                    await session.execute(text("""
                        UPDATE users SET role = 'user' WHERE role IS NULL
                    """))
                    
                    # 添加索引
                    await session.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)
                    """))
                    
                    await session.commit()
                    print("✅ 数据库架构更新完成")
                else:
                    print("✅ 数据库架构检查通过")
                
                return True
                
            except Exception as e:
                print(f"❌ 数据库架构初始化失败: {e}")
                await session.rollback()
                return False


# 全局实例
admin_init_service = AdminInitializationService()
