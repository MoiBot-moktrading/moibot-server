"""
FastAPI 애플리케이션 진입점
앱 초기화, DB 셋업, 라우터 등록을 담당한다.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import init_db
from api.router import router
from bot.bot_manager import bot_manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """앱 시작/종료 시 실행되는 lifespan 이벤트 핸들러"""
    # 앱 시작: DB 초기화 → 실행 중 봇 자동 재개
    await init_db()
    await bot_manager.resume_running_bots()
    yield
    # 앱 종료: 모든 봇 중지
    for bot_id in list(bot_manager._tasks.keys()):
        await bot_manager.stop(bot_id)


# FastAPI 앱 생성
app = FastAPI(
    title="MoiBot API",
    description="Upbit 모의투자 봇 엔진 REST API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 설정 (개발 환경: 모든 출처 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
