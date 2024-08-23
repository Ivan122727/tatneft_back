from typing import Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from tatneft_back.core.enumerations import UserRoles

from tatneft_back.models.user import User
from tatneft_back.services.user import get_user


async def get_current_user(*, ac: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> Optional[User]:
    user = await get_user(token=ac.credentials)
    if user is None:
        return None
    user.misc_data['current_token'] = ac.credentials
    if user is None:
        return None
    return user


async def get_strict_current_user(user: User = Depends(get_current_user)) -> User:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="no user")
    return user


def make_strict_depends_on_roles(roles: UserRoles):
    def wrapper(current_user: User = Depends(get_strict_current_user)) -> User:
        if not current_user.compare_roles(roles):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"not current_user.compare_roles(roles)"
            )
        return current_user

    return wrapper
