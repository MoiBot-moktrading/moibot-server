"""
API 라우터 통합 모듈
각 도메인별 라우터를 여기서 조립해 main.py에 노출한다.
"""

from fastapi import APIRouter

# 메인 라우터 — main.py에서 prefix="/api/v1"로 include한다
router = APIRouter()
