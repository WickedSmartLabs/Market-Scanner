import httpx
from datetime import datetime, timezone

BASE_URL = "https://api.binance.com"

def fetch_klines(
    symbol: str = "BTCUSDT",
    interval: str = "1m",
    limit: int = 200,
):
    """
    Binance klines endpoint.
    Normalizes to:
      {timestamp, open, high, low, close, volume}
    timestamp is UTC datetime.
    """
    url = f"{BASE_URL}/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}

    with httpx.Client(timeout=15.0) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        rows = r.json()

    candles = []
    for row in rows:
        # row[0] = open time in ms
        ts = datetime.fromtimestamp(row[0] / 1000.0, tz=timezone.utc).replace(tzinfo=None)
        candles.append({
            "timestamp": ts,
            "open": float(row[1]),
            "high": float(row[2]),
            "low": float(row[3]),
            "close": float(row[4]),
            "volume": float(row[5]),
        })

    return candles
