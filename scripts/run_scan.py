import json
import numpy as np
from scanner.config.watchlist import WATCHLIST
from scanner.config.versions import FEATURE_VERSION, SCORING_VERSION
from scanner.analysis.analyze_symbol import analyze_symbol
from scanner.storage.db import SessionLocal
from scanner.storage.analysis_models import AnalysisRun
from scanner.integrations.sheets import append_scan_results


def _to_json_safe(obj):
    if isinstance(obj, dict):
        return {k: _to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_json_safe(v) for v in obj]
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    return obj


def normalize_analysis_for_storage(analysis: dict) -> dict:
    summary = analysis["summary"]
    details = analysis["details"]

    return {
        "summary": _to_json_safe({
            **summary,
            "confidence": int(summary["confidence"]),
        }),
        "details": _to_json_safe({
            **details,
            "pause_detected":   bool(details["pause_detected"]),
            "volume_confirmed": bool(details.get("volume_confirmed", False)),
            "trend_slope": (
                float(details["trend_slope"])
                if details["trend_slope"] is not None else None
            ),
            "volatility": (
                float(details["volatility"])
                if details["volatility"] is not None else None
            ),
            "atr": (
                float(details["atr"])
                if details.get("atr") is not None else None
            ),
            "latest_close": (
                float(details["latest_close"])
                if details.get("latest_close") is not None else None
            ),
            "latest_volume": (
                float(details["latest_volume"])
                if details.get("latest_volume") is not None else None
            ),
            "reference_stop_distance": (
                float(details["reference_stop_distance"])
                if details.get("reference_stop_distance") is not None else None
            ),
            "distance_from_trend": [
                float(x) for x in details.get("distance_from_trend", [])
            ],
            "upper_wick_ratio": (
                float(details["upper_wick_ratio"])
                if details.get("upper_wick_ratio") is not None else None
            ),
            "lower_wick_ratio": (
                float(details["lower_wick_ratio"])
                if details.get("lower_wick_ratio") is not None else None
            ),
            "body_strength": (
                float(details["body_strength"])
                if details.get("body_strength") is not None else None
            ),
            "volume_ratio": (
                float(details["volume_ratio"])
                if details.get("volume_ratio") is not None else None
            ),
        }),
    }


def log_analysis(analysis: dict):
    normalized = normalize_analysis_for_storage(analysis)
    s = normalized["summary"]
    d = normalized["details"]

    session = SessionLocal()
    try:
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
            upper_wick_ratio=d.get("upper_wick_ratio"),
            lower_wick_ratio=d.get("lower_wick_ratio"),
            body_strength=d.get("body_strength"),
            candles_confirming=d.get("candles_confirming"),
            range_expansion=d.get("range_expansion"),
            vwap_relationship=d.get("vwap_relationship"),
            options_fit=d.get("options_fit"),
            volume_ratio=d.get("volume_ratio"),
            vpa_signal=d.get("vpa_signal"),
            feature_version=FEATURE_VERSION,
            scoring_version=SCORING_VERSION,
            summary=s,
            details=d,
        )
        session.add(row)
        session.commit()
    finally:
        session.close()


def _format_direction(direction: str) -> str:
    icons = {"Up": "↑", "Down": "↓", "Sideways": "→", "Unknown": "?"}
    return icons.get(direction, direction)


def _format_options(fit: str) -> str:
    icons = {"good": "🟢 good", "mediocre": "🟡 mediocre", "poor": "🔴 poor"}
    return icons.get(fit, f"  {fit}")


def _format_vpa(vpa: dict) -> str:
    if not vpa:
        return "unclear"
    signal   = vpa.get("signal", "unclear")
    strength = vpa.get("strength", "")
    icons = {
        "validation":           "✅ validation",
        "anomaly":              "⚠️  anomaly",
        "stopping_volume":      "🛑 stopping vol",
        "no_demand":            "📉 no demand",
        "upper_wick_rejection": "👆 upper wick",
        "lower_wick_rejection": "👇 lower wick",
        "unclear":              "❓ unclear",
    }
    label = icons.get(signal, signal)
    return f"{label} ({strength})" if strength and strength != "none" else label


def _print_symbol_block(a: dict):
    s = a["summary"]
    d = a["details"]

    price     = f"${d['latest_close']:>10.2f}" if d.get("latest_close") else "        N/A"
    atr       = f"ATR ${d['atr']:.2f}" if d.get("atr") else ""
    stop      = f"stop ${d['reference_stop_distance']:.2f}" if d.get("reference_stop_distance") else ""
    vol_r     = f"vol {d['volume_ratio']:.2f}x" if d.get("volume_ratio") else ""
    vwap      = f"VWAP {d.get('vwap_relationship', '?')}"
    body      = f"body {d['body_strength']:.2f}" if d.get("body_strength") else ""
    opts      = _format_options(d.get("options_fit", "?"))
    vpa       = _format_vpa(d.get("vpa_signal"))
    conf      = s["confidence"]
    conf_bar  = "█" * conf + "░" * (10 - conf)
    direction = _format_direction(s["direction"])

    print(f"  ┌─ {s['symbol']:10}  {direction}  [{conf_bar}] {conf}/10  {price}  {s['asset_class']}")
    print(f"  │  Trend: {d.get('trend_regime','?'):12}  Volatility: {d.get('volatility_regime','?'):8}  {vwap}  {vol_r}")
    print(f"  │  Candles: {body:12}  Range: {d.get('range_expansion','?'):12}  {atr}  {stop}")
    print(f"  │  Options: {opts:20}  VPA: {vpa}")

    vpa_note = (d.get("vpa_signal") or {}).get("vpa_note", "")
    if vpa_note:
        print(f"  │  Note: {vpa_note}")

    print(f"  └─ Setup: {s.get('setup', 'None')}")
    print()


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

    status_rank = {"This is important": 2, "Getting interesting": 1, "Low priority": 0}
    results.sort(
        key=lambda a: (status_rank[a["summary"]["status"]], a["summary"]["confidence"]),
        reverse=True,
    )

    important   = [r for r in results if r["summary"]["status"] == "This is important"]
    interesting = [r for r in results if r["summary"]["status"] == "Getting interesting"]
    low_pri     = [r for r in results if r["summary"]["status"] == "Low priority"]

    print()
    print("╔" + "═" * 78 + "╗")
    print(f"║  SAGE MARKET SCANNER  —  {len(results)} symbols  —  v{FEATURE_VERSION}/{SCORING_VERSION}".ljust(79) + "║")
    print("╚" + "═" * 78 + "╝")

    if important:
        print(f"\n  🔴  THIS IS IMPORTANT ({len(important)})")
        print("  " + "─" * 76)
        for a in important:
            _print_symbol_block(a)

    if interesting:
        print(f"\n  🟡  GETTING INTERESTING ({len(interesting)})")
        print("  " + "─" * 76)
        for a in interesting:
            _print_symbol_block(a)

    if low_pri:
        print(f"\n  ⚪  LOW PRIORITY ({len(low_pri)})")
        print("  " + "─" * 76)
        for a in low_pri:
            s = a["summary"]
            d = a["details"]
            price     = f"${d['latest_close']:.2f}" if d.get("latest_close") else "N/A"
            direction = _format_direction(s["direction"])
            vpa       = (d.get("vpa_signal") or {}).get("signal", "?")
            print(f"  → {s['symbol']:10} {direction}  {s['confidence']}/10  {price:>10}  {s.get('timeframe','?')}  vpa: {vpa}")

    # Sync to Google Sheets
    print()
    print("  Syncing to Google Sheets...", end=" ", flush=True)
    synced = append_scan_results(results)
    print("✓ done" if synced else "✗ failed")

    print()
    print("═" * 80)
    print()


if __name__ == "__main__":
    run_scan()
