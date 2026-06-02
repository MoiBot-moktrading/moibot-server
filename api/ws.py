"""WebSocket 실시간 스트리밍 엔드포인트"""

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from db.database import get_db

logger = logging.getLogger(__name__)

# prefix는 main.py에서 /ws로 붙임
router = APIRouter()

PUSH_INTERVAL = 15  # 초


@router.websocket("/live/{bot_id}")
async def ws_live(websocket: WebSocket, bot_id: int) -> None:
    """봇 실시간 포트폴리오 스트림"""
    await websocket.accept()
    logger.info(f"WS 연결 (bot_id={bot_id})")
    try:
        # 연결 시 히스토리 전송 (오래된 순 → 최신 순)
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT balance, position, pnl, snapshot_at "
                "FROM portfolio_snapshots WHERE bot_id = ? "
                "ORDER BY snapshot_at DESC LIMIT 100",
                (bot_id,),
            )
            rows = await cursor.fetchall()
        history = list(reversed([dict(row) for row in rows]))
        await websocket.send_json({"type": "history", "data": history})

        # 주기적 업데이트
        while True:
            await asyncio.sleep(PUSH_INTERVAL)
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT balance, position, pnl, snapshot_at "
                    "FROM portfolio_snapshots WHERE bot_id = ? "
                    "ORDER BY snapshot_at DESC LIMIT 1",
                    (bot_id,),
                )
                row = await cursor.fetchone()
            if row:
                await websocket.send_json({"type": "update", "data": dict(row)})
    except WebSocketDisconnect:
        logger.info(f"WS 연결 해제 (bot_id={bot_id})")
    except Exception as e:
        logger.error(f"WS 오류 (bot_id={bot_id}): {e}")
