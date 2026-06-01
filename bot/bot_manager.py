"""
멀티봇 실행 관리자
asyncio Task 딕셔너리로 봇 생명주기 관리
"""

import asyncio
import logging

from bot.base_bot import TradingBot
from bot.bot_factory import create_bot
from db.database import get_db

logger = logging.getLogger(__name__)

BOT_INTERVAL = 60  # 봇 루프 주기 (초)


async def _run_loop(bot: TradingBot) -> None:
    """봇 실행 루프 — 예외 발생 시 로그 후 재시작"""
    logger.info(f"봇 {bot.bot_id} 루프 시작")
    while True:
        try:
            await bot.run_once()
        except asyncio.CancelledError:
            logger.info(f"봇 {bot.bot_id} 중지됨")
            await bot.market.close()
            break
        except Exception as e:
            logger.error(f"봇 {bot.bot_id} 오류 (재시작 예정): {e}")
        await asyncio.sleep(BOT_INTERVAL)


class BotManager:
    """멀티봇 asyncio Task 관리자"""

    def __init__(self) -> None:
        self._tasks: dict[int, asyncio.Task] = {}

    async def start(self, bot_id: int) -> None:
        """봇 시작 — 이미 실행 중이면 무시"""
        if bot_id in self._tasks and not self._tasks[bot_id].done():
            logger.info(f"봇 {bot_id} 이미 실행 중")
            return

        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM bots WHERE id = ?", (bot_id,))
            row = await cursor.fetchone()
            if row is None:
                logger.error(f"봇 {bot_id} DB에 없음")
                return
            bot_row = dict(row)

        balance, position = await self._load_portfolio(bot_id)
        bot = create_bot(bot_row, balance=balance, position=position)
        task = asyncio.create_task(_run_loop(bot))
        self._tasks[bot_id] = task
        logger.info(f"봇 {bot_id} Task 생성 완료")

    async def stop(self, bot_id: int) -> None:
        """봇 중지"""
        task = self._tasks.pop(bot_id, None)
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        logger.info(f"봇 {bot_id} 중지 완료")

    async def resume_running_bots(self) -> None:
        """앱 재시작 시 DB status='running' 봇 자동 재개"""
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM bots WHERE status = 'running'")
            rows = await cursor.fetchall()
        for row in rows:
            await self.start(row["id"])
        logger.info(f"재개된 봇 수: {len(rows)}")

    async def _load_portfolio(self, bot_id: int) -> tuple[float, float]:
        """최신 포트폴리오 스냅샷에서 잔고/포지션 로드"""
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT balance, position FROM portfolio_snapshots WHERE bot_id = ? ORDER BY snapshot_at DESC LIMIT 1",
                (bot_id,),
            )
            row = await cursor.fetchone()
        if row:
            return row["balance"], row["position"]
        return 1_000_000.0, 0.0  # 초기 잔고


# 모듈 싱글턴
bot_manager = BotManager()
