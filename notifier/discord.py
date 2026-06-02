"""Discord 웹훅 매매 알림 전송 모듈"""

import asyncio
import logging

import requests

from config import DISCORD_WEBHOOK_URL

logger = logging.getLogger(__name__)

# 매수: cyan, 매도: red
_COLOR_BUY = 0x00B4D8
_COLOR_SELL = 0xEF4444


async def notify_trade(
    side: str,
    bot_id: int,
    symbol: str,
    price: float,
    amount: float,
    pnl: float | None = None,
) -> None:
    """매매 체결 Discord 알림 (DISCORD_WEBHOOK_URL 미설정 시 무시)"""
    if not DISCORD_WEBHOOK_URL:
        return

    if side == "buy":
        title = f"🟢 매수 체결 — Bot #{bot_id}"
        color = _COLOR_BUY
    else:
        title = f"🔴 매도 체결 — Bot #{bot_id}"
        color = _COLOR_SELL

    description = (
        f"**심볼:** {symbol}\n"
        f"**가격:** {price:,.0f} KRW\n"
        f"**수량:** {amount:.6f}"
    )
    if pnl is not None:
        sign = "+" if pnl >= 0 else ""
        description += f"\n**손익:** {sign}{pnl:,.0f} KRW"

    payload = {
        "embeds": [
            {
                "title": title,
                "description": description,
                "color": color,
            }
        ]
    }

    def _post() -> None:
        try:
            requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        except Exception as e:
            logger.warning(f"Discord 알림 전송 실패: {e}")

    # 블로킹 HTTP 요청을 스레드풀에서 실행 (봇 루프 차단 방지)
    asyncio.create_task(asyncio.to_thread(_post))
