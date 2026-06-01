"""
API 라우터 통합 모듈
각 도메인별 라우터를 여기서 조립해 main.py에 노출한다.
"""

from fastapi import APIRouter
from api import bots

router = APIRouter()
router.include_router(bots.router)
