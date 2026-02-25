from typing import Optional
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from .models import CricketPrediction, FootballPrediction

async def get_latest_football(db: AsyncSession, key: Optional[str], date: Optional[str]):
    q = select(FootballPrediction).order_by(desc(FootballPrediction.id))
    if key:
        q = q.where(FootballPrediction.key == key)
    if date:
        q = q.where(FootballPrediction.date == date)
    q = q.limit(100)
    res = await db.execute(q)
    return res.scalars().first()

async def get_latest_cricket(db: AsyncSession, key: Optional[str], date: Optional[str]):
    q = select(CricketPrediction).order_by(desc(CricketPrediction.id))
    if key:
        q = q.where(CricketPrediction.key == key)
    if date:
        q = q.where(CricketPrediction.date == date)
    q = q.limit(100)
    res = await db.execute(q)
    return res.scalars().first()
