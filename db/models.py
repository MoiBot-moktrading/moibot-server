"""
DB 테이블에 대응하는 Pydantic 모델 정의
Request(입력) / Response(출력) 용도로 분리한다.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ────────────────────────────────────────────────
# bots 테이블
# ────────────────────────────────────────────────

class BotCreate(BaseModel):
    """봇 생성 요청 모델"""
    name: str = Field(min_length=1, max_length=50)
    strategy: str
    symbol: str = Field(min_length=1)


class BotResponse(BaseModel):
    """봇 조회 응답 모델"""
    id: int
    name: str
    strategy: str
    symbol: str
    status: str
    created_at: Optional[datetime] = None


# ────────────────────────────────────────────────
# trades 테이블
# ────────────────────────────────────────────────

class TradeCreate(BaseModel):
    """거래 기록 생성 요청 모델"""
    bot_id: int
    side: str       # 'buy' 또는 'sell'
    price: float
    amount: float


class TradeResponse(BaseModel):
    """거래 기록 조회 응답 모델"""
    id: int
    bot_id: int
    side: str
    price: float
    amount: float
    executed_at: Optional[datetime] = None


# ────────────────────────────────────────────────
# portfolio_snapshots 테이블
# ────────────────────────────────────────────────

class PortfolioSnapshotCreate(BaseModel):
    """포트폴리오 스냅샷 생성 요청 모델"""
    bot_id: int
    balance: float
    position: float
    pnl: float


class PortfolioSnapshotResponse(BaseModel):
    """포트폴리오 스냅샷 조회 응답 모델"""
    id: int
    bot_id: int
    balance: float
    position: float
    pnl: float
    snapshot_at: Optional[datetime] = None
