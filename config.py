"""
애플리케이션 설정값 로드 모듈
python-dotenv를 사용해 .env 파일에서 환경변수를 읽어온다.
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


def _require(key: str) -> str:
    """필수 환경변수 읽기 — 없으면 예외 발생"""
    value = os.getenv(key)
    if not value:
        raise ValueError(f"환경변수 '{key}'가 설정되지 않았습니다. .env 파일을 확인하세요.")
    return value


# Upbit API 인증 키
UPBIT_ACCESS_KEY: str = _require("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY: str = _require("UPBIT_SECRET_KEY")

# Discord 웹훅 URL
DISCORD_WEBHOOK_URL: str = _require("DISCORD_WEBHOOK_URL")

# SQLite DB 파일 경로 (기본값: ./trading.db)
DATABASE_URL: str = os.getenv("DATABASE_URL", "./trading.db")
