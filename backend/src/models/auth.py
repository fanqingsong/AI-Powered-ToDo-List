from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: EmailStr
    display_name: Optional[str] = None


class UserCreate(UserBase):
    """用户创建模型"""
    password: str


class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    """用户模型"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: Optional[int] = None
    username: Optional[str] = None


class UserSessionBase(BaseModel):
    """用户会话基础模型"""
    session_name: Optional[str] = None


class UserSessionCreate(UserSessionBase):
    """用户会话创建模型"""
    pass


class UserSessionUpdate(UserSessionBase):
    """用户会话更新模型"""
    is_active: Optional[bool] = None


class UserSession(UserSessionBase):
    """用户会话模型"""
    id: int
    user_id: int
    session_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_activity: datetime

    class Config:
        from_attributes = True


class UserSessionList(BaseModel):
    """用户会话列表模型"""
    sessions: List[UserSession]
    total: int
