"""거래 이력 조회 API"""

import logging
from fastapi import APIRouter, Query
from db.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("/{bot_id}", response_model=dict)
async def get_trades(bot_id: int, limit: int = Query(default=50, ge=1, le=500)) -> dict:
    """봇의 거래 이력 조회 (최신순)"""
    try:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM trades WHERE bot_id = ? ORDER BY executed_at DESC LIMIT ?",
                (bot_id, limit),
            )
            rows = await cursor.fetchall()
        trades = [dict(row) for row in rows]
        return {"success": True, "data": trades, "message": "거래 이력 조회 성공"}
    except Exception as e:
        logger.error(f"거래 이력 조회 실패 (bot_id={bot_id}): {e}")
        return {"success": False, "data": None, "message": f"조회 실패: {str(e)}"}
