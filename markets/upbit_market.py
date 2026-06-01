"""
Upbit 거래소 어댑터 — ccxt async_support 사용
Public API 전용 (API 키 불필요)
"""

import ccxt.async_support as ccxt

from markets.base_market import BaseMarket


class UpbitMarket(BaseMarket):
    """Upbit ccxt 어댑터"""

    def __init__(self) -> None:
        self.exchange = ccxt.upbit({"enableRateLimit": True})

    async def fetch_ohlcv(self, symbol: str, timeframe: str = "1m", limit: int = 50) -> list[list]:
        """OHLCV 캔들 조회"""
        return await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

    async def fetch_ticker(self, symbol: str) -> dict:
        """현재 시세 조회"""
        return await self.exchange.fetch_ticker(symbol)

    async def close(self) -> None:
        """거래소 연결 종료"""
        await self.exchange.close()
