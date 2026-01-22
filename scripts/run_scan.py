from scanner.config.watchlist import WATCHLIST
from scanner.analysis.analyze_symbol import analyze_symbol
from scanner.storage.db import SessionLocal
from scanner.storage.analysis_models import AnalysisRun
from scanner.alerts.discord import send_alert


def normalize_analysis_for_storage(analysis: dict) -> dict:
    """
    Convert all values to JSON-safe native Python types.
    """
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


def log_analysis(analysis: dict):
    normalized = normalize_analysis_for_storage(analysis)
    s = normalized["summary"]
    d = normalized["details"]

    session = SessionLocal()

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
    session.close()


def run_scan():
    results = []

    for asset_class, items in WATCHLIST.items():
        for item in items:
            analysis = analyze_symbol(
                symbol=item["symbol"],
                asset_class=asset_class,
                timeframe=item["timeframe"],
                limit=200,
            )

            # Persist every analysis
            log_analysis(analysis)
            results.append(analysis)

            # Alert ONLY when attention is critical
            if analysis["summary"]["status"] == "This is important":
                send_alert(analysis["summary"])

    # Rank results by attention first, then confidence
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

    # Console output (top results only)
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
