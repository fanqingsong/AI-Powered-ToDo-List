from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from ..services.auth_service import AuthService
from ..models.auth import User, TokenData

# HTTP Bearer 认证
security = HTTPBearer(auto_error=False)  # 设置为不自动抛出错误

# 全局认证服务实例
auth_service = AuthService()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    try:
        token_data = auth_service.verify_token(credentials.credentials)
        if token_data is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    user = await auth_service.get_user_by_id(token_data.user_id)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_optional_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """获取当前用户（可选）"""
    if not credentials:
        return None
    
    try:
        token_data = auth_service.verify_token(credentials.credentials)
        if token_data is None:
            return None
        
        user = await auth_service.get_user_by_id(token_data.user_id)
        return user
    except Exception:
        return None
