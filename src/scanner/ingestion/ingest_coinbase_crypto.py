from sqlalchemy.dialects.postgresql import insert
from scanner.storage.db import SessionLocal
from scanner.storage.models import Candle
from scanner.connectors.coinbase.crypto import fetch_candles

def ingest_product(product: str, timeframe="1m"):
    session = SessionLocal()
    candles = fetch_candles(product, granularity=60, limit=300)

    for c in candles:
        stmt = insert(Candle).values(
            symbol=product.replace("-", "/"),
            asset_class="crypto",
            timeframe=timeframe,
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
    ingest_product("BTC-USD")
