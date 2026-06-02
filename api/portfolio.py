"""포트폴리오 스냅샷 조회 API"""

import logging
from fastapi import APIRouter
from db.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/{bot_id}", response_model=dict)
async def get_portfolio(bot_id: int) -> dict:
    """봇의 최신 포트폴리오 스냅샷 조회"""
    try:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM portfolio_snapshots WHERE bot_id = ? ORDER BY snapshot_at DESC LIMIT 1",
                (bot_id,),
            )
            row = await cursor.fetchone()
        if row is None:
            return {"success": False, "data": None, "message": "포트폴리오 데이터 없음"}
        return {"success": True, "data": dict(row), "message": "포트폴리오 조회 성공"}
    except Exception as e:
        logger.error(f"포트폴리오 조회 실패 (bot_id={bot_id}): {e}")
        return {"success": False, "data": None, "message": f"조회 실패: {str(e)}"}
