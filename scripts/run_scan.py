from datetime import datetime, timedelta

from scanner.config.watchlist import WATCHLIST
from scanner.analysis.analyze_symbol import analyze_symbol
from scanner.storage.db import SessionLocal
from scanner.storage.analysis_models import AnalysisRun
from scanner.alerts.discord import send_alert


ALERT_COOLDOWN_MINUTES = 30


def normalize_analysis_for_storage(analysis: dict) -> dict:
    summary = analysis["summary"]
    details = analysis["details"]

    return {
        "summary": {
            **summary,
            "confidence": int(summary["confidence"]),
        },
        "details": {
            **details,
            "pause_detected": bool(details["pause_detected"]),
            "trend_slope": (
                float(details["trend_slope"])
                if details["trend_slope"] is not None
                else None
            ),
            "volatility": (
                float(details["volatility"])
                if details["volatility"] is not None
                else None
            ),
            "distance_from_trend": [
                float(x) for x in details.get("distance_from_trend", [])
            ],
        },
    }


def log_analysis(session, analysis: dict):
    normalized = normalize_analysis_for_storage(analysis)
    s = normalized["summary"]
    d = normalized["details"]

    row = AnalysisRun(
        symbol=s["symbol"],
        asset_class=s["asset_class"],
        timeframe=s["timeframe"],
        status=s["status"],
        confidence=int(s["confidence"]),
        trend_regime=d["trend_regime"],
        volatility_regime=d["volatility_regime"],
        pause_detected=bool(d["pause_detected"]),
        trend_slope=d["trend_slope"],
        volatility=d["volatility"],
        summary=s,
        details=d,
    )

    session.add(row)
    session.commit()


def should_send_alert(session, summary: dict) -> bool:
    cutoff = datetime.utcnow() - timedelta(minutes=ALERT_COOLDOWN_MINUTES)

    recent_alert = (
        session.query(AnalysisRun)
        .filter(
            AnalysisRun.symbol == summary["symbol"],
            AnalysisRun.timeframe == summary["timeframe"],
            AnalysisRun.status == "This is important",
            AnalysisRun.created_at >= cutoff,
        )
        .order_by(AnalysisRun.created_at.desc())
        .first()
    )

    return recent_alert is None


def run_scan():
    session = SessionLocal()
    results = []

    for asset_class, items in WATCHLIST.items():
        for item in items:
            analysis = analyze_symbol(
                symbol=item["symbol"],
                asset_class=asset_class,
                timeframe=item["timeframe"],
                limit=200,
            )

            log_analysis(session, analysis)
            results.append(analysis)

            # Alert only if critical AND not recently alerted
            if analysis["summary"]["status"] == "This is important":
                if should_send_alert(session, analysis["summary"]):
                    send_alert(analysis["summary"])

    session.close()

    # Rank results by attention, then confidence
    status_rank = {
        "This is important": 2,
        "Getting interesting": 1,
        "Low priority": 0,
    }

    results.sort(
        key=lambda a: (
            status_rank[a["summary"]["status"]],
            a["summary"]["confidence"],
        ),
        reverse=True,
    )

    print("\nTop results:\n")
    for a in results[:10]:
        s = a["summary"]
        print(
            f"{s['status']:18} | "
            f"{s['confidence']:2}/10 | "
            f"{s['asset_class']:6} | "
            f"{s['symbol']:10} | "
            f"{s['timeframe']:3} | "
            f"{s['direction']:9} | "
            f"{s['market_activity']}"
        )


if __name__ == "__main__":
    run_scan()
