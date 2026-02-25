from typing import Optional, Dict, Any,List
from fastapi import APIRouter, Depends, Query, HTTPException, status,Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, update

from source.core.database import get_db
from source.app.auth.deps import auth_admin
from source.app.admin.models import Pipeline, PipelineStatus
from source.app.admin.schemas import PipelineCreate, PipelineUpdate, PipelineOut

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth_admin)],
    include_in_schema=True
)

ORDERABLE = {
    "first_name": 'u.first_name',
    "last_name": 'u.last_name',
    "email": 'u.email',
    "user_create_date": 'u.create_date',
    "subscription_date": 's.create_date',
    "status": 's.status',
}

@router.get("/users-subscriptions")
async def list_users_subscriptions(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    email: Optional[str] = Query(None, description="Filter by email (ILIKE)"),
    status_filter: Optional[str] = Query(None, description="Filter by subscription status"),
    order_by: str = Query("user_create_date", description=f"One of: {', '.join(ORDERABLE.keys())}"),
    order_dir: str = Query("desc", regex="^(?i)(asc|desc)$"),
):
    """
    Admin-only: list users with subscription details.
    """

    where_clauses = []
    params: Dict[str, Any] = {"limit": limit, "offset": offset}

    if email:
        where_clauses.append("u.email ILIKE :email")
        params["email"] = f"%{email}%"

    if status_filter:
        where_clauses.append("s.status = :status_filter")
        params["status_filter"] = status_filter

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    order_col = ORDERABLE.get(order_by)
    if not order_col:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid order_by. Allowed: {', '.join(ORDERABLE.keys())}",
        )
    order_dir_sql = "ASC" if order_dir.lower() == "asc" else "DESC"

    data_sql = text(f"""
        SELECT
            u.first_name,
            u.last_name,
            u.email,
            u.create_date,
            u.last_login_ip,
            u.last_seen_at,
            u.geo_country,
            u.geo_region,
            u.geo_city,
            u.geo_latitude,
            u.geo_longitude,
            u.source,
            s.create_date AS subscription_date,
            s.payment_method_id,
            s.payment_method_type,
            s.status,
            s.next_billing_at,
            s.last_order_id
        FROM "User" AS u
        LEFT JOIN subscription AS s
            ON s.user_id = u.id
        {where_sql}
        ORDER BY {order_col} {order_dir_sql}, u.id ASC
        LIMIT :limit OFFSET :offset
    """)

    count_sql = text(f"""
        SELECT COUNT(*)::bigint
        FROM "User" AS u
        LEFT JOIN subscription AS s
            ON s.user_id = u.id
        {where_sql}
    """)

    result = await db.execute(data_sql, params)
    rows = [dict(r._mapping) for r in result.fetchall()]

    total = (
        await db.execute(
            count_sql,
            {k: v for k, v in params.items() if k in ("email", "status_filter")},
        )
    ).scalar_one()

    return {
        "count": int(total),
        "limit": limit,
        "offset": offset,
        "order_by": order_by,
        "order_dir": order_dir.lower(),
        "results": rows,
    }



@router.get("/jobs", response_model=list[PipelineOut], summary="List pipelines")
async def list_pipelines(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: Optional[PipelineStatus] = Query(None),
    pipeline_type: Optional[str] = Query(None),
    order_by: str = Query("start_time"),  # start_time|end_time|create_date|update_date
    order_dir: str = Query("desc"),       # asc|desc
):
    ORDER_MAP = {
        "start_time": Pipeline.start_time,
        "end_time": Pipeline.end_time,
        "create_date": Pipeline.create_date,
        "update_date": Pipeline.update_date,
        "status": Pipeline.status,
        "pipeline_type": Pipeline.pipeline_type,
    }
    col = ORDER_MAP.get(order_by, Pipeline.start_time)
    col = col.desc() if order_dir.lower() == "desc" else col.asc()

    stmt = select(Pipeline)
    if status:
        stmt = stmt.filter(Pipeline.status == status)
    if pipeline_type:
        stmt = stmt.filter(Pipeline.pipeline_type == pipeline_type)
    stmt = stmt.order_by(col).limit(limit).offset(offset)

    rows = (await db.execute(stmt)).scalars().all()
    return rows