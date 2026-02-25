from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from source.app.access.models import Role, Permission, UserSettings, user_roles, role_permissions
from source.app.access.schemas import (
    RoleCreate, PermissionCreate,
    UserSettingsUpdate
)

# Roles

async def create_role(db: AsyncSession, data: RoleCreate) -> Role:
    role = Role(name=data.name, description=data.description)
    if data.permission_ids:
        permissions = (await db.execute(
            select(Permission).where(Permission.id.in_(data.permission_ids))
        )).scalars().all()
        role.permissions = permissions
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role

# similar: get_role, list_roles, update_role, delete_role

# Permissions

async def create_permission(db: AsyncSession, data: PermissionCreate) -> Permission:
    perm = Permission(name=data.name, description=data.description)
    db.add(perm)
    await db.commit()
    await db.refresh(perm)
    return perm

# similar: list_permissions

# User Settings

async def get_or_create_settings(db: AsyncSession, user_id: int) -> UserSettings:
    settings = (await db.execute(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )).scalar_one_or_none()
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings

async def update_settings(
    db: AsyncSession, user_id: int, data: UserSettingsUpdate
) -> UserSettings:
    settings = await get_or_create_settings(db, user_id)
    for field, val in data.dict(exclude_unset=True).items():
        setattr(settings, field, val)
    db.add(settings)
    await db.commit()
    await db.refresh(settings)
    return settings
