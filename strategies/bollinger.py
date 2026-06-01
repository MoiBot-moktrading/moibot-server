"""
볼린저 밴드 전략
종가 < 하단밴드: BUY, 종가 > 상단밴드: SELL
"""

import math
from strategies.base_strategy import BaseStrategy, Signal


def _bollinger(closes: list[float], period: int = 20, std_dev: float = 2.0) -> tuple[float, float, float]:
    """볼린저 밴드 계산 → (상단, 중단, 하단)"""
    recent = closes[-period:]
    mid = sum(recent) / period
    variance = sum((x - mid) ** 2 for x in recent) / period
    std = math.sqrt(variance)
    return mid + std_dev * std, mid, mid - std_dev * std


class BollingerStrategy(BaseStrategy):
    """볼린저 밴드 전략"""

    PERIOD: int = 20
    STD_DEV: float = 2.0
    MIN_CANDLES: int = PERIOD

    def calculate(self, ohlcv: list[list]) -> Signal:
        if not self._has_enough(ohlcv):
            return Signal.HOLD

        closes = self._closes(ohlcv)
        current_price = closes[-1]
        upper, _mid, lower = _bollinger(closes, self.PERIOD, self.STD_DEV)

        if current_price < lower:
            return Signal.BUY
        if current_price > upper:
            return Signal.SELL
        return Signal.HOLD
