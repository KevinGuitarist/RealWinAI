from math import ceil

from sqlalchemy import asc, desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from source.app.users.enums import Order, Sort
from source.app.users.models import User
from source.app.users.schemas import (
    UserCreate,
    UserPage,
    UserRequest,
    UserUpdate,
    UserUpdateRequest,
)
import uuid

async def create_user(user: UserRequest, db: AsyncSession) -> User | None:
    try:
        user = User(**UserCreate(**user.model_dump()).model_dump())
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    except IntegrityError:
        return None


async def update_user(
    user_id,
    request: UserUpdateRequest,
    db: AsyncSession,
) -> User | None:
    try:
        user = await db.scalar(select(User).filter_by(id=int(user_id)))
        fields_to_update = UserUpdate(**request.model_dump()).model_dump().items()
        for key, value in fields_to_update:
            if value is not None:
                setattr(user, key, value)
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        return None


async def delete_user(user_id, db: AsyncSession) -> None:

    user = await db.scalar(select(User).filter_by(id=int(user_id)))
    await db.delete(user)
    await db.commit()
    return None

async def impersonate_user(user_id, db: AsyncSession) -> User:

    user = await db.scalar(select(User).filter_by(id=int(user_id)))
    return user


async def list_users(
    page: int, size: int, sort: Sort, order: Order, db: AsyncSession
) -> UserPage:
    order = asc(sort) if order == Order.ASC else desc(sort)

    users = await db.scalars(
        select(User).order_by(order).offset((page - 1) * size).limit(size)
    )
    total = await db.scalar(select(func.count(User.id)))

    return UserPage(
        users=users,
        page=page,
        size=size,
        total=total,
        pages=(ceil(total / size)),
    )
