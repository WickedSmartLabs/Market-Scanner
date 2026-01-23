import os
import requests
from dotenv import load_dotenv

# Explicitly load .env so this works under cron and subprocesses
load_dotenv(dotenv_path=".env")

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def send_alert(summary: dict):
    if not WEBHOOK_URL:
        return

    message = (
        f"**{summary['status']}**\n"
        f"Symbol: {summary['symbol']} ({summary['timeframe']})\n"
        f"Direction: {summary['direction']}\n"
        f"Market activity: {summary['market_activity']}\n"
        f"Confidence: {summary['confidence']}/10"
    )

    requests.post(
        WEBHOOK_URL,
        json={"content": message},
        timeout=5,
    )
