from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from source.core.database import get_db
from source.app.auth.auth import CurrentUser, Admin
from source.app.access import services, schemas

access_router = APIRouter(prefix="/access", tags=["Access Control"],include_in_schema=False)

@access_router.post(
    "/permissions",
    response_model=schemas.PermissionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_permission(
    data: schemas.PermissionCreate,
    current_admin: Admin,
    db: AsyncSession = Depends(get_db),
):
    return await services.create_permission(db, data)

@access_router.get(
    "/permissions",
    response_model=list[schemas.PermissionRead],
)
async def list_permissions(
    current_admin: Admin,
    db: AsyncSession = Depends(get_db),
):
    return await services.list_permissions(db)

@access_router.post(
    "/roles",
    response_model=schemas.RoleRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    data: schemas.RoleCreate,
    current_admin: Admin,
    db: AsyncSession = Depends(get_db),
):
    return await services.create_role(db, data)

@access_router.get(
    "/roles",
    response_model=list[schemas.RoleRead],
)
async def list_roles(
    current_admin: Admin,
    db: AsyncSession = Depends(get_db),
):
    return await services.list_roles(db)

@access_router.get(
    "/settings",
    response_model=schemas.UserSettingsRead,
)
async def read_my_settings(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    return await services.get_or_create_settings(db, current_user.id)

@access_router.patch(
    "/settings",
    response_model=schemas.UserSettingsRead,
)
async def update_my_settings(
    data: schemas.UserSettingsUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    return await services.update_settings(db, current_user.id, data)
