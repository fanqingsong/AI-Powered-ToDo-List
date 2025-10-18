import asyncio
import uuid
import hashlib
from typing import Optional, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy import select, update, delete, func, and_, desc
from sqlalchemy.orm import selectinload

from ..database import get_db_session, AsyncSessionLocal
from ..models.auth import (
    User, UserCreate, UserUpdate, UserLogin, Token, TokenData,
    UserSession, UserSessionCreate, UserSessionUpdate, UserSessionList
)
from ..models.database_models import UserDB, UserSessionDB

# JWT配置
SECRET_KEY = "your-secret-key-change-in-production"  # 在生产环境中应该使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    """用户认证服务"""
    
    def __init__(self):
        pass
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        # 使用简单的SHA256哈希（仅用于演示，生产环境应使用bcrypt）
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
    
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希"""
        # 使用简单的SHA256哈希（仅用于演示，生产环境应使用bcrypt）
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get("sub")
            username: str = payload.get("username")
            
            if user_id is None or username is None:
                return None
            
            return TokenData(user_id=user_id, username=username)
        except JWTError:
            return None
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户"""
        async with get_db_session() as session:
            query = select(UserDB).where(UserDB.username == username)
            result = await session.execute(query)
            user_db = result.scalar_one_or_none()
            
            if not user_db:
                return None
            
            if not self.verify_password(password, user_db.password_hash):
                return None
            
            # 在session关闭前提取所有需要的属性
            user_data = {
                'id': user_db.id,
                'username': user_db.username,
                'email': user_db.email,
                'display_name': user_db.display_name,
                'is_active': user_db.is_active,
                'created_at': user_db.created_at,
                'updated_at': user_db.updated_at,
                'last_login': user_db.last_login
            }
            
            # 暂时不更新last_login，避免数据库连接问题
            # user_db.last_login = datetime.utcnow()
            # await session.commit()
            
            # 使用提取的数据创建User对象
            return User(**user_data)
    
    async def create_user(self, user_create: UserCreate) -> User:
        """创建用户"""
        async with get_db_session() as session:
            # 检查用户名和邮箱是否已存在
            existing_query = select(UserDB).where(
                (UserDB.username == user_create.username) | 
                (UserDB.email == user_create.email)
            )
            existing_result = await session.execute(existing_query)
            existing_user = existing_result.scalar_one_or_none()
            
            if existing_user:
                if existing_user.username == user_create.username:
                    raise ValueError("用户名已存在")
                else:
                    raise ValueError("邮箱已存在")
            
            # 创建新用户
            user_db = UserDB(
                username=user_create.username,
                email=user_create.email,
                password_hash=self.get_password_hash(user_create.password),
                display_name=user_create.display_name or user_create.username
            )
            
            session.add(user_db)
            await session.flush()
            
            return User(
                id=user_db.id,
                username=user_db.username,
                email=user_db.email,
                display_name=user_db.display_name,
                is_active=user_db.is_active,
                created_at=user_db.created_at,
                updated_at=user_db.updated_at,
                last_login=user_db.last_login
            )
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        async with get_db_session() as session:
            query = select(UserDB).where(UserDB.id == user_id)
            result = await session.execute(query)
            user_db = result.scalar_one_or_none()
            
            if not user_db:
                return None
            
            return User(
                id=user_db.id,
                username=user_db.username,
                email=user_db.email,
                display_name=user_db.display_name,
                is_active=user_db.is_active,
                created_at=user_db.created_at,
                updated_at=user_db.updated_at,
                last_login=user_db.last_login
            )
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        async with get_db_session() as session:
            query = select(UserDB).where(UserDB.username == username)
            result = await session.execute(query)
            user_db = result.scalar_one_or_none()
            
            if not user_db:
                return None
            
            return User(
                id=user_db.id,
                username=user_db.username,
                email=user_db.email,
                display_name=user_db.display_name,
                is_active=user_db.is_active,
                created_at=user_db.created_at,
                updated_at=user_db.updated_at,
                last_login=user_db.last_login
            )
    
    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """更新用户"""
        async with get_db_session() as session:
            query = select(UserDB).where(UserDB.id == user_id)
            result = await session.execute(query)
            user_db = result.scalar_one_or_none()
            
            if not user_db:
                return None
            
            # 更新字段
            if user_update.username is not None:
                user_db.username = user_update.username
            if user_update.email is not None:
                user_db.email = user_update.email
            if user_update.display_name is not None:
                user_db.display_name = user_update.display_name
            if user_update.password is not None:
                user_db.password_hash = self.get_password_hash(user_update.password)
            
            user_db.updated_at = datetime.utcnow()
            await session.commit()
            
            return User(
                id=user_db.id,
                username=user_db.username,
                email=user_db.email,
                display_name=user_db.display_name,
                is_active=user_db.is_active,
                created_at=user_db.created_at,
                updated_at=user_db.updated_at,
                last_login=user_db.last_login
            )


class UserSessionService:
    """用户会话管理服务"""
    
    async def create_session(self, user_id: int, session_name: Optional[str] = None) -> UserSession:
        """创建用户会话"""
        async with get_db_session() as session:
            session_id = f"session_{uuid.uuid4().hex}"
            
            user_session_db = UserSessionDB(
                user_id=user_id,
                session_id=session_id,
                session_name=session_name or f"会话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            
            session.add(user_session_db)
            await session.flush()
            
            return UserSession(
                id=user_session_db.id,
                user_id=user_session_db.user_id,
                session_id=user_session_db.session_id,
                session_name=user_session_db.session_name,
                is_active=user_session_db.is_active,
                created_at=user_session_db.created_at,
                updated_at=user_session_db.updated_at,
                last_activity=user_session_db.last_activity
            )
    
    async def get_user_sessions(self, user_id: int, limit: int = 20) -> UserSessionList:
        """获取用户的所有会话"""
        async with get_db_session() as session:
            query = select(UserSessionDB).where(
                UserSessionDB.user_id == user_id
            ).order_by(desc(UserSessionDB.last_activity)).limit(limit)
            
            result = await session.execute(query)
            sessions_db = result.scalars().all()
            
            sessions = []
            for session_db in sessions_db:
                sessions.append(UserSession(
                    id=session_db.id,
                    user_id=session_db.user_id,
                    session_id=session_db.session_id,
                    session_name=session_db.session_name,
                    is_active=session_db.is_active,
                    created_at=session_db.created_at,
                    updated_at=session_db.updated_at,
                    last_activity=session_db.last_activity
                ))
            
            # 获取总数
            count_query = select(func.count(UserSessionDB.id)).where(
                UserSessionDB.user_id == user_id
            )
            count_result = await session.execute(count_query)
            total = count_result.scalar() or 0
            
            return UserSessionList(sessions=sessions, total=total)
    
    async def get_session_by_id(self, session_id: str) -> Optional[UserSession]:
        """根据会话ID获取会话"""
        async with get_db_session() as session:
            query = select(UserSessionDB).where(UserSessionDB.session_id == session_id)
            result = await session.execute(query)
            session_db = result.scalar_one_or_none()
            
            if not session_db:
                return None
            
            return UserSession(
                id=session_db.id,
                user_id=session_db.user_id,
                session_id=session_db.session_id,
                session_name=session_db.session_name,
                is_active=session_db.is_active,
                created_at=session_db.created_at,
                updated_at=session_db.updated_at,
                last_activity=session_db.last_activity
            )
    
    async def update_session_activity(self, session_id: str) -> bool:
        """更新会话活动时间"""
        async with get_db_session() as session:
            query = update(UserSessionDB).where(
                UserSessionDB.session_id == session_id
            ).values(
                last_activity=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            result = await session.execute(query)
            return result.rowcount > 0
    
    async def delete_session(self, session_id: str, user_id: int) -> bool:
        """删除会话"""
        async with get_db_session() as session:
            query = delete(UserSessionDB).where(
                and_(
                    UserSessionDB.session_id == session_id,
                    UserSessionDB.user_id == user_id
                )
            )
            
            result = await session.execute(query)
            return result.rowcount > 0
