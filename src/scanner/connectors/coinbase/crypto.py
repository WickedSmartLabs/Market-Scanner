import httpx
from datetime import datetime, timezone

BASE_URL = "https://api.exchange.coinbase.com"

def fetch_candles(
    product: str = "BTC-USD",
    granularity: int = 60,
    limit: int = 200,
):
    """
    Coinbase candles:
    [ time, low, high, open, close, volume ]
    Returns normalized dicts.
    """
    url = f"{BASE_URL}/products/{product}/candles"
    params = {"granularity": granularity}

    with httpx.Client(timeout=15.0) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        rows = r.json()

    candles = []
    for row in reversed(rows[:limit]):  # ascending time
        ts = datetime.fromtimestamp(row[0], tz=timezone.utc).replace(tzinfo=None)
        candles.append({
            "timestamp": ts,
            "open": float(row[3]),
            "high": float(row[2]),
            "low": float(row[1]),
            "close": float(row[4]),
            "volume": float(row[5]),
        })
    return candles
