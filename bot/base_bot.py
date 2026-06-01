"""
모의투자 봇 — 시세 조회 → 전략 신호 → 모의 주문 → DB 기록
"""

import logging
from datetime import datetime

from db.database import get_db
from markets.base_market import BaseMarket
from strategies.base_strategy import BaseStrategy, Signal

logger = logging.getLogger(__name__)

INITIAL_BALANCE = 1_000_000.0  # 모의투자 초기 잔고 (KRW)
BUY_RATIO = 0.95               # 매수 시 잔고 사용 비율


class TradingBot:
    """모의투자 봇"""

    def __init__(
        self,
        bot_id: int,
        symbol: str,
        strategy: BaseStrategy,
        market: BaseMarket,
        balance: float = INITIAL_BALANCE,
        position: float = 0.0,
    ) -> None:
        self.bot_id = bot_id
        self.symbol = symbol
        self.strategy = strategy
        self.market = market
        self.balance = balance
        self.position = position
        self.initial_balance = INITIAL_BALANCE

    async def run_once(self) -> None:
        """한 틱 실행 — OHLCV 조회 → 신호 계산 → 모의 주문 → DB 기록"""
        try:
            ohlcv = await self.market.fetch_ohlcv(self.symbol, "1m", limit=50)
            ticker = await self.market.fetch_ticker(self.symbol)
            current_price: float = ticker["last"]

            signal = self.strategy.calculate(ohlcv)

            if signal == Signal.BUY and self.position == 0.0:
                await self._buy(current_price)
            elif signal == Signal.SELL and self.position > 0.0:
                await self._sell(current_price)

            await self._save_snapshot(current_price)

        except Exception as e:
            logger.error(f"봇 {self.bot_id} 틱 오류: {e}")

    async def _buy(self, price: float) -> None:
        """모의 매수"""
        amount = (self.balance * BUY_RATIO) / price
        cost = amount * price
        self.balance -= cost
        self.position += amount

        async with get_db() as db:
            await db.execute(
                "INSERT INTO trades (bot_id, side, price, amount, executed_at) VALUES (?, ?, ?, ?, ?)",
                (self.bot_id, "buy", price, amount, datetime.utcnow()),
            )
            await db.commit()
        logger.info(f"봇 {self.bot_id} 매수: {amount:.6f} @ {price:,.0f}")

    async def _sell(self, price: float) -> None:
        """모의 매도"""
        proceeds = self.position * price
        self.balance += proceeds
        sold_amount = self.position
        self.position = 0.0

        async with get_db() as db:
            await db.execute(
                "INSERT INTO trades (bot_id, side, price, amount, executed_at) VALUES (?, ?, ?, ?, ?)",
                (self.bot_id, "sell", price, sold_amount, datetime.utcnow()),
            )
            await db.commit()
        logger.info(f"봇 {self.bot_id} 매도: {sold_amount:.6f} @ {price:,.0f}")

    async def _save_snapshot(self, current_price: float) -> None:
        """포트폴리오 스냅샷 저장"""
        total_value = self.balance + self.position * current_price
        pnl = total_value - self.initial_balance

        async with get_db() as db:
            await db.execute(
                "INSERT INTO portfolio_snapshots (bot_id, balance, position, pnl, snapshot_at) VALUES (?, ?, ?, ?, ?)",
                (self.bot_id, self.balance, self.position, pnl, datetime.utcnow()),
            )
            await db.commit()
