def format_analysis(analysis: dict) -> str:
    s = analysis["summary"]
    d = analysis["details"]

    lines = []

    # --- Summary ---
    lines.append(f"Market Summary — {s['symbol']} ({s['timeframe']})")
    lines.append("")
    lines.append(f"Direction: {s['direction']}")
    lines.append(f"Market activity: {s['market_activity']}")
    lines.append(f"Setup detected: {s['setup']}")
    lines.append(f"Confidence: {s['confidence']} / 10")
    lines.append(f"Status: {s['status']}")

    # --- Details ---
    lines.append("\nWhy this matters:")
    for note in d["notes"]:
        lines.append(f"- {note}")

    lines.append("\nKey measurements:")
    lines.append(f"- Candles analyzed: {d['candles_loaded']}")
    lines.append(f"- Trend slope (20): {d['trend_slope']}")
    lines.append(f"- Volatility (20): {d['volatility']}")
    lines.append(f"- Trend regime: {d['trend_regime']}")
    lines.append(f"- Volatility regime: {d['volatility_regime']}")

    return "\n".join(lines)
