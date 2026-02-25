from typing import List, Optional
from sqlalchemy import Text, bindparam, String, Integer,Date,String,and_,Numeric, cast,case,select,Float,literal,or_
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from source.app.predictions.models import CricketPrediction,FootballPrediction
from source.core.database import get_db
from source.app.predictions.services import get_latest_cricket,get_latest_football
from source.app.predictions.schemas import PredictionOut,FootballPredictionOut,CricketPredictionOut
import json
import datetime as dt
from sqlalchemy.sql import func
from source.app.auth.auth import CurrentUser
from sqlalchemy.dialects.postgresql import JSONB


CP = CricketPrediction


predictions_router = APIRouter(prefix="/predictions", tags=["Predictions"])

FP = FootballPrediction  # e.g., class FootballPrediction(Base): __tablename__ = "football_predictions"

@predictions_router.get("/football", response_model=List[FootballPredictionOut])
async def get_football_predictions(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    key: Optional[str] = Query(None),
    date: Optional[str] = Query(None, description="YYYY-MM-DD"),
):
    # Parse date safely
    date_obj: Optional[dt.date] = None
    if date:
        try:
            date_obj = dt.date.fromisoformat(date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    j = FP.prediction  # JSONB column

    # Top-level attributes
    match_name = j.op('->>')('Match Name').label('match_name')
    match_kick_off = j.op('->>')('Match/Kick Off Time').label('match_kick_off')

    # Nested prediction fields
    pred_winner_raw = j.op('->')('prediction').op('->>')('predicted_winner')
    predicted_winner = pred_winner_raw.label('predicted_winner')

    probs = j.op('->')('prediction').op('->')('probabilitiesr')
    prob_home_txt = probs.op('->>')('home')
    prob_away_txt = probs.op('->>')('away')
    prob_draw_txt = probs.op('->>')('draw')

    teams = j.op('->')('prediction').op('->')('teams')
    team_home = teams.op('->>')('home')
    team_away = teams.op('->>')('away')

    # Case-insensitive compare like your lower(trim(...)) in SQL
    pw_lc   = func.lower(func.trim(pred_winner_raw))
    home_lc = func.lower(team_home)
    away_lc = func.lower(team_away)

    win_prob_txt = case(
        (pw_lc == 'home', prob_home_txt),
        (pw_lc == 'away', prob_away_txt),
        (pw_lc == 'draw', prob_draw_txt),
        (pw_lc == home_lc, prob_home_txt),
        (pw_lc == away_lc, prob_away_txt),
        else_=None,
    )

    win_probability_percent = cast(win_prob_txt, Float).label('win_probability_percent')

    logos = j.op('->')('Logos').label('logos')
    prediction_object = j.op('->')('prediction').label('prediction_object')

    # Build the query
    stmt = (
        select(
            FP.id,
            FP.key,
            match_name,
            match_kick_off,
            predicted_winner,
            win_probability_percent,
            logos,
            prediction_object,
        )
        .select_from(FP)
        .order_by(FP.id.desc())
        .limit(limit)
        .offset(offset)
    )

    if key is not None:
        stmt = stmt.where(FP.key == key)
    if date_obj is not None:
        # If FP.date is a timestamp, cast it to DATE to compare
        stmt = stmt.where(cast(FP.date, Date) == date_obj)

    res = await db.execute(stmt)
    rows = res.mappings().all()

    out: List[FootballPredictionOut] = []
    for r in rows:
        pred_obj = r["prediction_object"]
        if isinstance(pred_obj, (bytes, bytearray, memoryview)):
            pred_obj = pred_obj.decode()
        if isinstance(pred_obj, str):
            try:
                pred_obj = json.loads(pred_obj)
            except Exception:
                pass

        logos_obj = r.get("logos")
        if isinstance(logos_obj, (bytes, bytearray, memoryview)):
            logos_obj = logos_obj.decode()
        if isinstance(logos_obj, str):
            try:
                logos_obj = json.loads(logos_obj)
            except Exception:
                pass

        out.append(FootballPredictionOut(
            id=r["id"],
            key=r["key"],
            logos=logos_obj,
            match_name=r.get("match_name"),
            match_kick_off=r.get("match_kick_off"),
            predicted_winner=r.get("predicted_winner"),
            win_probability_percent=r.get("win_probability_percent"),
            prediction_object=pred_obj,
        ))

    return out


@predictions_router.get("/cricket", response_model=List[CricketPredictionOut])

async def get_cricket_predictions(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    key: Optional[str] = Query(None),
    date: Optional[str] = Query(None, description="YYYY-MM-DD"),
):
    if date:
        try:
            date_obj = dt.date.fromisoformat(date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    else:
        date_obj = dt.now().strftime('%Y-%m-%d')

    j = CP.prediction  # may be jsonb or text

    def sanitized_jsonb(text_expr):
        cleaned = func.regexp_replace(text_expr, r"\\'", "'", 'g')
        return cast(cleaned, JSONB)

    root_json = case(
        (func.jsonb_typeof(j) == literal('object'), j),
        else_=cast(cast(j, Text), JSONB)
    )

    match_raw = root_json.op('->')('match')
    match_json = case(
        (func.jsonb_typeof(match_raw) == literal('object'), match_raw),
        else_=cast(root_json.op('->>')('match'), JSONB)
    )

    pred_wrap_raw = root_json.op('->')('prediction')
    pred_wrap = case(
        (func.jsonb_typeof(pred_wrap_raw) == literal('object'), pred_wrap_raw),
        else_=cast(root_json.op('->>')('prediction'), JSONB)
    )

    match_mi = case(
        (func.jsonb_typeof(match_json.op('->')('match_info')) == literal('object'), match_json.op('->')('match_info')),
        else_=cast(match_json.op('->>')('match_info'), JSONB)
    )
    pred_mi = case(
        (func.jsonb_typeof(pred_wrap.op('->')('match_info')) == literal('object'), pred_wrap.op('->')('match_info')),
        else_=cast(pred_wrap.op('->>')('match_info'), JSONB)
    )

    match_insights = match_mi.op('->')('insights')
    pred_insights  = pred_mi.op('->')('insights')

    match_pred = case(
        (func.jsonb_typeof(match_json.op('->')('prediction')) == literal('object'), match_json.op('->')('prediction')),
        else_=sanitized_jsonb(match_json.op('->>')('prediction'))
    )
    pred_pred = case(
        (func.jsonb_typeof(pred_wrap.op('->')('prediction')) == literal('object'), pred_wrap.op('->')('prediction')),
        else_=sanitized_jsonb(pred_wrap.op('->>')('prediction'))
    )

    match_name = func.coalesce(
        match_insights.op('->>')('name'),
        pred_insights.op('->>')('name'),
        func.concat_ws(
            ' vs ',
            match_pred.op('->')('teams').op('->>')('a_name'),
            match_pred.op('->')('teams').op('->>')('b_name')
        ),
        func.concat_ws(
            ' vs ',
            pred_pred.op('->')('teams').op('->>')('a_name'),
            pred_pred.op('->')('teams').op('->>')('b_name')
        )
    ).label('match_name')

    match_kick_off = func.coalesce(
        func.to_timestamp(cast(match_insights.op('->>')('start_at'), Numeric)),
        func.to_timestamp(match_mi.op('->>')('match_time'), literal('YYYY-MM-DD HH24:MI "UTC"')),
        func.to_timestamp(cast(pred_insights.op('->>')('start_at'), Numeric)),
        func.to_timestamp(pred_mi.op('->>')('match_time'), literal('YYYY-MM-DD HH24:MI "UTC"')),
        func.to_timestamp(match_pred.op('->')('match_metadata').op('->>')('match_time'), literal('YYYY-MM-DD HH24:MI "UTC"')),
        func.to_timestamp(pred_pred.op('->')('match_metadata').op('->>')('match_time'), literal('YYYY-MM-DD HH24:MI "UTC"'))
    ).label('match_kick_off')

    explanation = func.coalesce(
        match_pred.op('->>')('explanation'),
        pred_pred.op('->>')('explanation')
    ).label('explanation')

    winner_code = func.coalesce(
        match_pred.op('->')('prediction').op('->>')('winner'),
        pred_pred.op('->')('prediction').op('->>')('winner')
    )
    a_name = func.coalesce(
        match_pred.op('->')('teams').op('->>')('a_name'),
        pred_pred.op('->')('teams').op('->>')('a_name')
    )
    b_name = func.coalesce(
        match_pred.op('->')('teams').op('->>')('b_name'),
        pred_pred.op('->')('teams').op('->>')('b_name')
    )

    predicted_winner = case(
        (winner_code == 'A', a_name),
        (winner_code == 'B', b_name),
        else_=None
    ).label('predicted_winner')

    a_win_pct = cast(func.coalesce(
        match_pred.op('->')('prediction').op('->>')('a_win_pct'),
        pred_pred.op('->')('prediction').op('->>')('a_win_pct')
    ), Numeric)
    b_win_pct = cast(func.coalesce(
        match_pred.op('->')('prediction').op('->>')('b_win_pct'),
        pred_pred.op('->')('prediction').op('->>')('b_win_pct')
    ), Numeric)

    win_probability = case(
        (winner_code == 'A', a_win_pct),
        (winner_code == 'B', b_win_pct),
        else_=None
    ).label('win_probability')

    prediction_object = func.coalesce(match_pred, pred_pred).label('prediction_object')

    # return raw match_date and match_time too
    match_date = func.coalesce(
        match_mi.op('->>')('match_date'),
        pred_mi.op('->>')('match_date')
    ).label('match_date')


    venue = func.coalesce(
        match_mi.op('->')('venue'),
        pred_mi.op('->')('venue')
    ).label('venue')


    match_time = func.coalesce(
        match_mi.op('->>')('match_time'),
        pred_mi.op('->>')('match_time')
    ).label('match_time')

    summary = func.coalesce(
        match_json.op('->')('ai_summary')
    ).label('ai_summary')

    # ---------- Base Query ----------
    stmt = select(
        match_name,
        summary,
        venue,
        match_kick_off,
        explanation,
        predicted_winner,
        win_probability,
        prediction_object,
        match_date,
        match_time
    ).select_from(CP)

    # filter only 2025-09-08 in match_time
    stmt = stmt.where(
        or_(
            match_mi.op('->>')('match_time').like(f'{date}%'),
            pred_mi.op('->>')('match_time').like(f'{date}%')
        )
    )

    if key:
        stmt = stmt.where(or_(
            match_insights.op('->>')('key') == key,
            match_mi.op('->>')('match_key') == key,
            pred_insights.op('->>')('key') == key,
            pred_mi.op('->>')('match_key') == key,
            match_pred.op('->>')('match_key') == key,
            pred_pred.op('->>')('match_key') == key,
        ))

    stmt = stmt.order_by(CP.id.desc()).limit(limit).offset(offset)

    res = await db.execute(stmt)
    rows = res.mappings().all()

    out: List[CricketPredictionOut] = []
    for r in rows:
        pred_obj = r["prediction_object"]
        if isinstance(pred_obj, (bytes, bytearray, memoryview)):
            pred_obj = pred_obj.decode()
        if isinstance(pred_obj, str):
            try:
                pred_obj = json.loads(pred_obj)
            except Exception:
                pass

        win_prob = r.get("win_probability")
        if win_prob is not None:
            try:
                win_prob = float(win_prob)
            except Exception:
                pass

        out.append(CricketPredictionOut(
            match_name=r.get("match_name"),
            venue=r.get("venue"),
            summary=r.get("ai_summary"),
            match_kick_off=r.get("match_kick_off"),
            explanation=r.get("explanation"),
            predicted_winner=r.get("predicted_winner"),
            win_probability=win_prob,
            prediction_object=pred_obj,
            match_date=r.get("match_date"),
            match_time=r.get("match_time"),
        ))
        
    return out