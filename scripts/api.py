"""
Market Scanner -- API layer.
Exposes scanner results from PostgreSQL for Sage and other consumers.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.scanner.storage.analysis_models import AnalysisRun

DATABASE_URL = "postgresql+psycopg://scanner:scanner@localhost:5432/market_scanner"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI(title="Market Scanner API", version="1.0.0")


@app.get("/scanner/latest")
def get_latest():
    """Return the most recent scan result for each symbol."""
    session = SessionLocal()
    try:
        results = (
            session.query(AnalysisRun)
            .order_by(AnalysisRun.created_at.desc())
            .limit(10)
            .all()
        )

        if not results:
            return {"status": "no_data", "signals": []}

        signals = []
        for r in results:
            signals.append({
                "symbol":           r.symbol,
                "timeframe":        r.timeframe,
                "asset_class":      r.asset_class,
                "bias":             r.trend_regime,
                "confidence":       r.confidence,
                "price":            r.entry_price,
                "trend_state":      r.trend_regime,
                "volatility_state": r.volatility_regime,
                "pause_detected":   r.pause_detected,
                "trend_slope":      r.trend_slope,
                "volatility":       r.volatility,
                "volume":           r.entry_volume,
                "status_label":     r.status,
                "summary":          r.summary,
                "details":          r.details,
                "scanned_at":       r.created_at.isoformat() if r.created_at else None,
            })

        return {
            "status": "ok",
            "count": len(signals),
            "signals": signals,
        }
    finally:
        session.close()


@app.get("/scanner/latest/{symbol}")
def get_latest_for_symbol(symbol: str):
    """Return the most recent scan result for a specific symbol."""
    session = SessionLocal()
    try:
        result = (
            session.query(AnalysisRun)
            .filter(AnalysisRun.symbol == symbol.upper())
            .order_by(AnalysisRun.created_at.desc())
            .first()
        )

        if not result:
            return {"status": "no_data", "symbol": symbol}

        return {
            "status":           "ok",
            "symbol":           result.symbol,
            "timeframe":        result.timeframe,
            "asset_class":      result.asset_class,
            "bias":             result.trend_regime,
            "confidence":       result.confidence,
            "price":            result.entry_price,
            "trend_state":      result.trend_regime,
            "volatility_state": result.volatility_regime,
            "pause_detected":   result.pause_detected,
            "trend_slope":      result.trend_slope,
            "volatility":       result.volatility,
            "volume":           result.entry_volume,
            "status_label":     result.status,
            "summary":          result.summary,
            "details":          result.details,
            "scanned_at":       result.created_at.isoformat() if result.created_at else None,
        }
    finally:
        session.close()


@app.get("/scanner/history")
def get_history(limit: int = 10):
    """Return recent scan history across all symbols."""
    session = SessionLocal()
    try:
        results = (
            session.query(AnalysisRun)
            .order_by(AnalysisRun.created_at.desc())
            .limit(limit)
            .all()
        )

        if not results:
            return {"status": "no_data", "signals": []}

        signals = []
        for r in results:
            signals.append({
                "symbol":       r.symbol,
                "timeframe":    r.timeframe,
                "bias":         r.trend_regime,
                "confidence":   r.confidence,
                "status_label": r.status,
                "price":        r.entry_price,
                "scanned_at":   r.created_at.isoformat() if r.created_at else None,
            })

        return {
            "status":  "ok",
            "count":   len(signals),
            "signals": signals,
        }
    finally:
        session.close()


@app.get("/scanner/health")
def health():
    """Return ingestion health and last successful scan timestamp."""
    session = SessionLocal()
    try:
        latest = (
            session.query(AnalysisRun)
            .order_by(AnalysisRun.created_at.desc())
            .first()
        )

        if not latest:
            return {
                "status":    "degraded",
                "last_scan": None,
                "message":   "No scan results found in database.",
            }

        last_scan = latest.created_at
        now = datetime.now(timezone.utc)
        age_minutes = int(
            (now - last_scan.replace(tzinfo=timezone.utc)).total_seconds() // 60
        )

        return {
            "status":      "ok" if age_minutes < 15 else "stale",
            "last_scan":   last_scan.isoformat(),
            "age_minutes": age_minutes,
            "message":     "ok" if age_minutes < 15 else f"Last scan was {age_minutes} minutes ago.",
        }
    finally:
        session.close()
