"""
이동평균 크로스 전략
단기MA(5) > 장기MA(20): BUY, 단기MA < 장기MA: SELL
"""

from strategies.base_strategy import BaseStrategy, Signal


def _sma(values: list[float], period: int) -> float:
    """단순 이동 평균 계산"""
    return sum(values[-period:]) / period


class MACrossStrategy(BaseStrategy):
    """이동평균 크로스 전략"""

    SHORT_PERIOD: int = 5
    LONG_PERIOD: int = 20
    MIN_CANDLES: int = LONG_PERIOD + 1

    def calculate(self, ohlcv: list[list]) -> Signal:
        if not self._has_enough(ohlcv):
            return Signal.HOLD

        closes = self._closes(ohlcv)

        short_now = _sma(closes, self.SHORT_PERIOD)
        long_now = _sma(closes, self.LONG_PERIOD)
        short_prev = _sma(closes[:-1], self.SHORT_PERIOD)
        long_prev = _sma(closes[:-1], self.LONG_PERIOD)

        if short_prev <= long_prev and short_now > long_now:
            return Signal.BUY
        if short_prev >= long_prev and short_now < long_now:
            return Signal.SELL
        return Signal.HOLD
