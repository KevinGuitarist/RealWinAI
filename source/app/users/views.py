from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from source.app.auth.auth import Admin, CurrentUser
from source.app.users.models import User
from source.app.users.schemas import (
    UserPage,
    UserPagination,
    UserRequest,
    UserResponse,
    UserUpdateRequest)
from source.app.auth.services import generate_token

from source.app.users.services import create_user, delete_user, impersonate_user, list_users, update_user
from source.core.database import get_db
from source.core.exceptions import conflict
from source.core.schemas import ExceptionSchema

users_router = APIRouter(prefix="/users")

@users_router.get(
    "/",
    response_model=UserResponse,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema}},
    tags=["Users"],
    include_in_schema=False
)
async def user_get(user: CurrentUser) -> User:
    return user


