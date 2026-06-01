"""
거래소 어댑터 추상 기반 클래스
"""

from abc import ABC, abstractmethod


class BaseMarket(ABC):
    """거래소 인터페이스"""

    @abstractmethod
    async def fetch_ohlcv(self, symbol: str, timeframe: str = "1m", limit: int = 50) -> list[list]:
        """
        OHLCV 캔들 데이터 조회
        반환: [[timestamp, open, high, low, close, volume], ...]
        """
        ...

    @abstractmethod
    async def fetch_ticker(self, symbol: str) -> dict:
        """
        현재 시세 조회
        반환 딕셔너리에 'last' 키로 현재가 포함
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """거래소 연결 종료"""
        ...
