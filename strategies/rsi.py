"""
RSI 전략
RSI(14) < 30: BUY, RSI(14) > 70: SELL
"""

from strategies.base_strategy import BaseStrategy, Signal


def _rsi(closes: list[float], period: int = 14) -> float:
    """RSI 계산"""
    if len(closes) < period + 1:
        return 50.0

    gains, losses = [], []
    for i in range(1, period + 1):
        diff = closes[-period - 1 + i] - closes[-period - 2 + i]
        (gains if diff > 0 else losses).append(abs(diff))

    avg_gain = sum(gains) / period if gains else 0.0
    avg_loss = sum(losses) / period if losses else 0.0

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


class RSIStrategy(BaseStrategy):
    """RSI 과매수/과매도 전략"""

    PERIOD: int = 14
    OVERSOLD: float = 30.0
    OVERBOUGHT: float = 70.0
    MIN_CANDLES: int = PERIOD + 1

    def calculate(self, ohlcv: list[list]) -> Signal:
        if not self._has_enough(ohlcv):
            return Signal.HOLD

        closes = self._closes(ohlcv)
        rsi = _rsi(closes, self.PERIOD)

        if rsi < self.OVERSOLD:
            return Signal.BUY
        if rsi > self.OVERBOUGHT:
            return Signal.SELL
        return Signal.HOLD
