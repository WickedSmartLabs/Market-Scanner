from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Boolean, Float
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime


class Base(DeclarativeBase):
    pass


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    symbol: Mapped[str] = mapped_column(String, index=True)
    asset_class: Mapped[str] = mapped_column(String, index=True)
    timeframe: Mapped[str] = mapped_column(String, index=True)

    status: Mapped[str] = mapped_column(String, index=True)
    confidence: Mapped[int] = mapped_column(Integer, index=True)

    trend_regime: Mapped[str] = mapped_column(String)
    volatility_regime: Mapped[str] = mapped_column(String)
    pause_detected: Mapped[bool] = mapped_column(Boolean)

    trend_slope: Mapped[float | None] = mapped_column(Float, nullable=True)
    volatility: Mapped[float | None] = mapped_column(Float, nullable=True)

    # NEW: Price context
    entry_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    entry_volume: Mapped[float | None] = mapped_column(Float, nullable=True)

    # NEW: Outcome tracking
    outcome_evaluated: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    outcome: Mapped[str | None] = mapped_column(String, nullable=True)
    forward_return_15m: Mapped[float | None] = mapped_column(Float, nullable=True)
    forward_return_1h: Mapped[float | None] = mapped_column(Float, nullable=True)

    summary: Mapped[dict] = mapped_column(JSONB)
    details: Mapped[dict] = mapped_column(JSONB)
