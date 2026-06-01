"""
봇 인스턴스 생성 팩토리
DB row → TradingBot 인스턴스
"""

from bot.base_bot import TradingBot
from markets.upbit_market import UpbitMarket
from strategies.ma_cross import MACrossStrategy
from strategies.rsi import RSIStrategy
from strategies.bollinger import BollingerStrategy
from strategies.base_strategy import BaseStrategy


_STRATEGY_MAP: dict[str, type[BaseStrategy]] = {
    "ma_cross": MACrossStrategy,
    "rsi": RSIStrategy,
    "bollinger": BollingerStrategy,
}


def create_bot(bot_row: dict, balance: float = 1_000_000.0, position: float = 0.0) -> TradingBot:
    """
    DB bot row로부터 TradingBot 인스턴스 생성
    bot_row: {"id", "name", "strategy", "symbol", ...}
    """
    strategy_cls = _STRATEGY_MAP.get(bot_row["strategy"])
    if strategy_cls is None:
        raise ValueError(f"알 수 없는 전략: {bot_row['strategy']}")

    return TradingBot(
        bot_id=bot_row["id"],
        symbol=bot_row["symbol"],
        strategy=strategy_cls(),
        market=UpbitMarket(),
        balance=balance,
        position=position,
    )
