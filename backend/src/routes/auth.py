from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List

from ..models.auth import (
    User, UserCreate, UserUpdate, UserLogin, Token,
    UserSession, UserSessionCreate, UserSessionUpdate, UserSessionList
)
from ..services.auth_service import AuthService, UserSessionService
from ..auth.dependencies import get_current_active_user, get_optional_current_user

def create_auth_routes() -> APIRouter:
    """创建认证相关路由"""
    router = APIRouter()
    
    auth_service = AuthService()
    session_service = UserSessionService()
    
    @router.post("/register", response_model=User, status_code=201)
    async def register(user_create: UserCreate):
        """用户注册"""
        try:
            user = await auth_service.create_user(user_create)
            return user
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="注册失败"
            )
    
    @router.post("/login", response_model=Token)
    async def login(form_data: OAuth2PasswordRequestForm = Depends()):
        """用户登录"""
        user = await auth_service.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=30)
        access_token = auth_service.create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=30 * 60  # 30分钟
        )
    
    @router.get("/me", response_model=User)
    async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
        """获取当前用户信息"""
        return current_user
    
    @router.put("/me", response_model=User)
    async def update_current_user(
        user_update: UserUpdate,
        current_user: User = Depends(get_current_active_user)
    ):
        """更新当前用户信息"""
        try:
            updated_user = await auth_service.update_user(current_user.id, user_update)
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            return updated_user
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新失败"
            )
    
    # 用户会话管理
    @router.post("/sessions", response_model=UserSession, status_code=201)
    async def create_session(
        session_create: UserSessionCreate,
        current_user: User = Depends(get_current_active_user)
    ):
        """创建新会话"""
        try:
            session = await session_service.create_session(
                current_user.id, 
                session_create.session_name
            )
            return session
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建会话失败"
            )
    
    @router.get("/sessions", response_model=UserSessionList)
    async def get_user_sessions(
        limit: int = 20,
        current_user: User = Depends(get_current_active_user)
    ):
        """获取用户的所有会话"""
        try:
            sessions = await session_service.get_user_sessions(current_user.id, limit)
            return sessions
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取会话列表失败"
            )
    
    @router.get("/sessions/{session_id}", response_model=UserSession)
    async def get_session(
        session_id: str,
        current_user: User = Depends(get_current_active_user)
    ):
        """获取特定会话"""
        session = await session_service.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )
        
        # 检查会话是否属于当前用户
        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此会话"
            )
        
        return session
    
    @router.put("/sessions/{session_id}", response_model=UserSession)
    async def update_session(
        session_id: str,
        session_update: UserSessionUpdate,
        current_user: User = Depends(get_current_active_user)
    ):
        """更新会话"""
        # 这里可以实现会话更新逻辑
        # 目前先返回会话信息
        session = await session_service.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )
        
        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此会话"
            )
        
        return session
    
    @router.delete("/sessions/{session_id}")
    async def delete_session(
        session_id: str,
        current_user: User = Depends(get_current_active_user)
    ):
        """删除会话"""
        try:
            success = await session_service.delete_session(session_id, current_user.id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="会话不存在"
                )
            return {"message": "会话删除成功"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除会话失败"
            )
    
    return router
