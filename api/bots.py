"""
봇 CRUD API 엔드포인트
"""

from fastapi import APIRouter
from db.database import get_db
from db.models import BotCreate
from bot.bot_manager import bot_manager

router = APIRouter(prefix="/bots", tags=["bots"])

VALID_STRATEGIES = {"ma_cross", "rsi", "bollinger"}


@router.get("", response_model=dict)
async def get_bots() -> dict:
    """봇 전체 목록 조회"""
    try:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM bots ORDER BY created_at DESC")
            rows = await cursor.fetchall()
            bots = [dict(row) for row in rows]
        return {"success": True, "data": bots, "message": "봇 목록 조회 성공"}
    except Exception as e:
        # DB 오류 발생 시 에러 응답
        return {"success": False, "data": None, "message": f"봇 목록 조회 실패: {str(e)}"}


@router.post("", response_model=dict, status_code=201)
async def create_bot(body: BotCreate) -> dict:
    """봇 생성"""
    if body.strategy not in VALID_STRATEGIES:
        return {"success": False, "data": None, "message": f"전략은 {VALID_STRATEGIES} 중 하나여야 합니다"}

    try:
        async with get_db() as db:
            cursor = await db.execute(
                "INSERT INTO bots (name, strategy, symbol) VALUES (?, ?, ?)",
                (body.name, body.strategy, body.symbol),
            )
            await db.commit()
            bot_id = cursor.lastrowid
            cursor = await db.execute("SELECT * FROM bots WHERE id = ?", (bot_id,))
            row = await cursor.fetchone()

        # INSERT 후 SELECT에서 row가 None이면 에러 응답
        if row is None:
            return {"success": False, "data": None, "message": "봇 생성 후 조회 실패"}

        return {"success": True, "data": dict(row), "message": "봇 생성 성공"}
    except Exception as e:
        # DB 오류 발생 시 에러 응답
        return {"success": False, "data": None, "message": f"봇 생성 실패: {str(e)}"}


@router.patch("/{bot_id}/start", response_model=dict)
async def start_bot(bot_id: int) -> dict:
    """봇 시작 — status를 running으로 변경"""
    try:
        async with get_db() as db:
            cursor = await db.execute("SELECT id FROM bots WHERE id = ?", (bot_id,))
            row = await cursor.fetchone()
            if row is None:
                return {"success": False, "data": None, "message": "봇을 찾을 수 없습니다"}

            await db.execute(
                "UPDATE bots SET status = 'running' WHERE id = ?", (bot_id,)
            )
            await db.commit()
            cursor = await db.execute("SELECT * FROM bots WHERE id = ?", (bot_id,))
            updated = await cursor.fetchone()

            if updated is None:
                return {"success": False, "data": None, "message": "봇 업데이트 후 조회 실패"}

        try:
            await bot_manager.start(bot_id)
        except Exception as e:
            return {"success": False, "data": None, "message": f"봇 엔진 시작 실패: {str(e)}"}
        return {"success": True, "data": dict(updated), "message": "봇 시작됨"}
    except Exception as e:
        return {"success": False, "data": None, "message": f"봇 시작 실패: {str(e)}"}


@router.patch("/{bot_id}/stop", response_model=dict)
async def stop_bot(bot_id: int) -> dict:
    """봇 중지 — status를 stopped로 변경"""
    try:
        async with get_db() as db:
            cursor = await db.execute("SELECT id FROM bots WHERE id = ?", (bot_id,))
            row = await cursor.fetchone()
            if row is None:
                return {"success": False, "data": None, "message": "봇을 찾을 수 없습니다"}

            await db.execute(
                "UPDATE bots SET status = 'stopped' WHERE id = ?", (bot_id,)
            )
            await db.commit()
            cursor = await db.execute("SELECT * FROM bots WHERE id = ?", (bot_id,))
            updated = await cursor.fetchone()

            if updated is None:
                return {"success": False, "data": None, "message": "봇 업데이트 후 조회 실패"}

        try:
            await bot_manager.stop(bot_id)
        except Exception as e:
            return {"success": False, "data": None, "message": f"봇 엔진 중지 실패: {str(e)}"}
        return {"success": True, "data": dict(updated), "message": "봇 중지됨"}
    except Exception as e:
        return {"success": False, "data": None, "message": f"봇 중지 실패: {str(e)}"}
