from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional

from ..models.auth import (
    User, UserCreate, UserUpdate, UserList, UserDelete
)
from ..services.auth_service import AuthService
from ..auth.dependencies import get_current_active_user

def create_admin_routes() -> APIRouter:
    """创建管理员相关路由"""
    router = APIRouter()
    
    auth_service = AuthService()
    
    async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
        """获取当前管理员用户"""
        is_admin = await auth_service.is_admin(current_user.id)
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限"
            )
        return current_user
    
    @router.get("/users", response_model=UserList)
    async def get_all_users(
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        admin_user: User = Depends(get_current_admin_user)
    ):
        """获取所有用户列表（管理员功能）"""
        try:
            users = await auth_service.get_all_users(limit=limit, offset=offset)
            return users
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取用户列表失败"
            )
    
    @router.post("/users", response_model=User, status_code=201)
    async def create_user(
        user_create: UserCreate,
        admin_user: User = Depends(get_current_admin_user)
    ):
        """创建新用户（管理员功能）"""
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
                detail="创建用户失败"
            )
    
    @router.put("/users/{user_id}", response_model=User)
    async def update_user(
        user_id: int,
        user_update: UserUpdate,
        admin_user: User = Depends(get_current_admin_user)
    ):
        """更新用户信息（管理员功能）"""
        try:
            # 防止管理员修改自己的角色
            if admin_user.id == user_id and user_update.role is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能修改自己的角色"
                )
            
            updated_user = await auth_service.update_user(user_id, user_update)
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
                detail="更新用户失败"
            )
    
    @router.delete("/users/{user_id}")
    async def delete_user(
        user_id: int,
        admin_user: User = Depends(get_current_admin_user)
    ):
        """删除用户（管理员功能）"""
        try:
            # 防止管理员删除自己
            if admin_user.id == user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能删除自己的账户"
                )
            
            success = await auth_service.delete_user(user_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            return {"message": "用户删除成功"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除用户失败"
            )
    
    @router.get("/users/{user_id}", response_model=User)
    async def get_user_by_id(
        user_id: int,
        admin_user: User = Depends(get_current_admin_user)
    ):
        """根据ID获取用户信息（管理员功能）"""
        try:
            user = await auth_service.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            return user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取用户信息失败"
            )
    
    return router
