from scanner.config.watchlist import WATCHLIST
from scanner.analysis.analyze_symbol import analyze_symbol
from scanner.storage.db import SessionLocal
from scanner.storage.analysis_models import AnalysisRun


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
            "volume_confirmed": bool(details.get("volume_confirmed", False)),
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
            "atr": (
                float(details["atr"])
                if details.get("atr") is not None
                else None
            ),
            "latest_close": (
                float(details["latest_close"])
                if details.get("latest_close") is not None
                else None
            ),
            "latest_volume": (
                float(details["latest_volume"])
                if details.get("latest_volume") is not None
                else None
            ),
            "reference_stop_distance": (
                float(details["reference_stop_distance"])
                if details.get("reference_stop_distance") is not None
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
        entry_price=d.get("latest_close"),
        entry_volume=d.get("latest_volume"),
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

            results.append(analysis)
            log_analysis(analysis)

    # Rank by attention first, then confidence
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

    # Improved console output
    print("\n" + "=" * 80)
    print(f"SCAN COMPLETE - {len(results)} symbols analyzed")
    print("=" * 80)

    important = [r for r in results if r["summary"]["status"] == "This is important"]
    interesting = [r for r in results if r["summary"]["status"] == "Getting interesting"]

    if important:
        print(f"\n🔴 THIS IS IMPORTANT ({len(important)}):")
        for a in important:
            s = a["summary"]
            d = a["details"]
            price = f"${d.get('latest_close', 0):.2f}" if d.get('latest_close') else "N/A"
            stop = f"ATR: ${d.get('reference_stop_distance', 0):.2f}" if d.get('reference_stop_distance') else ""
            print(f"  → {s['symbol']:10} | {s['direction']:8} | Conf: {s['confidence']}/10 | {price:>10} | {stop}")

    if interesting:
        print(f"\n🟡 GETTING INTERESTING ({len(interesting)}):")
        for a in interesting:
            s = a["summary"]
            d = a["details"]
            price = f"${d.get('latest_close', 0):.2f}" if d.get('latest_close') else "N/A"
            print(f"  → {s['symbol']:10} | {s['direction']:8} | Conf: {s['confidence']}/10 | {price:>10}")

    low_pri = len(results) - len(important) - len(interesting)
    if low_pri > 0:
        print(f"\n⚪ LOW PRIORITY: {low_pri} symbols")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    run_scan()
