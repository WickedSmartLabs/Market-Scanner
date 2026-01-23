import httpx
from datetime import datetime, timezone, date, timedelta
from scanner.config.settings import POLYGON_API_KEY

BASE_URL = "https://api.polygon.io"

def fetch_daily_aggregates(
    ticker: str,
    limit: int = 50,
):
    """
    Polygon DAILY aggregates (free-tier friendly).

    Returns normalized candles:
      {timestamp, open, high, low, close, volume}
    """

    # Pull the last ~60 calendar days to ensure market days
    end = date.today()
    start = end - timedelta(days=60)

    url = (
        f"{BASE_URL}/v2/aggs/ticker/{ticker}"
        f"/range/1/day/{start.isoformat()}/{end.isoformat()}"
    )

    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": str(limit),
        "apiKey": POLYGON_API_KEY,
    }

    with httpx.Client(timeout=15.0) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    results = data.get("results") or []

    candles = []
    for row in results:
        ts = datetime.fromtimestamp(
            row["t"] / 1000.0, tz=timezone.utc
        ).replace(tzinfo=None)

        candles.append({
            "timestamp": ts,
            "open": float(row["o"]),
            "high": float(row["h"]),
            "low": float(row["l"]),
            "close": float(row["c"]),
            "volume": float(row.get("v", 0.0)),
        })

    return candles
