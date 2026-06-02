"""
애플리케이션 설정값 로드 모듈
python-dotenv를 사용해 .env 파일에서 환경변수를 읽어온다.
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Upbit API 인증 키 (공개 API는 불필요, 향후 실거래 확장용)
UPBIT_ACCESS_KEY: str | None = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY: str | None = os.getenv("UPBIT_SECRET_KEY")

# Discord 웹훅 URL (설정 없으면 알림 비활성화)
DISCORD_WEBHOOK_URL: str | None = os.getenv("DISCORD_WEBHOOK_URL")

# SQLite DB 파일 경로 (기본값: ./trading.db)
DATABASE_URL: str = os.getenv("DATABASE_URL", "./trading.db")
