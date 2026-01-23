from sqlalchemy.dialects.postgresql import insert
from scanner.storage.db import SessionLocal
from scanner.storage.models import Candle
from scanner.connectors.polygon.stocks import fetch_daily_aggregates

def ingest_symbol(ticker: str):
    session = SessionLocal()
    candles = fetch_daily_aggregates(ticker, limit=200)

    for c in candles:
        stmt = insert(Candle).values(
            symbol=ticker,
            asset_class="stock",
            timeframe="1d",
            timestamp=c["timestamp"],
            open=c["open"],
            high=c["high"],
            low=c["low"],
            close=c["close"],
            volume=c["volume"],
        ).on_conflict_do_nothing(
            index_elements=["symbol", "asset_class", "timeframe", "timestamp"]
        )
        session.execute(stmt)

    session.commit()
    session.close()

if __name__ == "__main__":
    ingest_symbol("AAPL")
