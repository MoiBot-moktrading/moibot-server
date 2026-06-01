"""
전략 기반 클래스 및 신호 정의
"""

from abc import ABC, abstractmethod
from enum import Enum


class Signal(Enum):
    """매매 신호"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class BaseStrategy(ABC):
    """모든 전략의 추상 기반 클래스"""

    MIN_CANDLES: int = 50

    @abstractmethod
    def calculate(self, ohlcv: list[list]) -> Signal:
        """
        OHLCV 데이터를 받아 매매 신호 반환
        ohlcv: [[timestamp, open, high, low, close, volume], ...]
        """
        ...

    def _closes(self, ohlcv: list[list]) -> list[float]:
        """종가 리스트 추출"""
        return [candle[4] for candle in ohlcv]

    def _has_enough(self, ohlcv: list[list]) -> bool:
        """최소 캔들 수 충족 여부"""
        return len(ohlcv) >= self.MIN_CANDLES
