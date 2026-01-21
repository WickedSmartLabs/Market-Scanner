from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Candle(Base):
    __tablename__ = "candles"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True, nullable=False)
    asset_class = Column(String, nullable=False)  # crypto, stock
    timeframe = Column(String, nullable=False)    # 1m, 5m, 1d
    timestamp = Column(DateTime, index=True, nullable=False)

    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
