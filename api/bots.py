"""
봇 CRUD API 엔드포인트
"""

from fastapi import APIRouter
from db.database import get_db
from db.models import BotCreate

router = APIRouter(prefix="/bots", tags=["bots"])

VALID_STRATEGIES = {"ma_cross", "rsi", "bollinger"}


@router.get("", response_model=dict)
async def get_bots() -> dict:
    """봇 전체 목록 조회"""
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM bots ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        bots = [dict(row) for row in rows]
    return {"success": True, "data": bots, "message": "봇 목록 조회 성공"}


@router.post("", response_model=dict, status_code=201)
async def create_bot(body: BotCreate) -> dict:
    """봇 생성"""
    if body.strategy not in VALID_STRATEGIES:
        return {"success": False, "data": None, "message": f"전략은 {VALID_STRATEGIES} 중 하나여야 합니다"}

    async with get_db() as db:
        cursor = await db.execute(
            "INSERT INTO bots (name, strategy, symbol) VALUES (?, ?, ?)",
            (body.name, body.strategy, body.symbol),
        )
        await db.commit()
        bot_id = cursor.lastrowid
        cursor = await db.execute("SELECT * FROM bots WHERE id = ?", (bot_id,))
        row = await cursor.fetchone()

    return {"success": True, "data": dict(row), "message": "봇 생성 성공"}
