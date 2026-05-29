"""
SQLite DB 연결 및 초기화 모듈
aiosqlite를 사용해 비동기 쿼리를 처리한다.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aiosqlite

from config import DATABASE_URL


async def init_db() -> None:
    """
    테이블이 없으면 생성하는 초기화 함수.
    앱 시작 시 lifespan에서 호출된다.
    """
    async with aiosqlite.connect(DATABASE_URL) as db:
        # 봇 설정 테이블
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bots (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                strategy   TEXT    NOT NULL,
                symbol     TEXT    NOT NULL,
                status     TEXT    NOT NULL DEFAULT 'stopped',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 체결 거래 이력 테이블
        await db.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id      INTEGER NOT NULL REFERENCES bots(id),
                side        TEXT    NOT NULL,
                price       REAL    NOT NULL,
                amount      REAL    NOT NULL,
                executed_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 포트폴리오 스냅샷 테이블
        await db.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id      INTEGER NOT NULL REFERENCES bots(id),
                balance     REAL    NOT NULL,
                position    REAL    NOT NULL,
                pnl         REAL    NOT NULL,
                snapshot_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.commit()


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """
    DB 연결을 반환하는 비동기 컨텍스트 매니저.
    사용 예시:
        async with get_db() as db:
            await db.execute(...)
    """
    async with aiosqlite.connect(DATABASE_URL) as db:
        # Row를 딕셔너리처럼 접근할 수 있도록 설정
        db.row_factory = aiosqlite.Row
        yield db
