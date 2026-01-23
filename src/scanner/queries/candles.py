from sqlalchemy import select, desc
from scanner.storage.db import SessionLocal
from scanner.storage.models import Candle

def get_recent_candles(
    symbol: str,
    asset_class: str,
    timeframe: str,
    limit: int = 200,
):
    """
    Fetch recent candles from Postgres, returned in chronological order.
    """
    session = SessionLocal()

    stmt = (
        select(Candle)
        .where(
            Candle.symbol == symbol,
            Candle.asset_class == asset_class,
            Candle.timeframe == timeframe,
        )
        .order_by(desc(Candle.timestamp))
        .limit(limit)
    )

    rows = session.execute(stmt).scalars().all()
    session.close()

    # reverse so oldest -> newest
    return list(reversed(rows))
