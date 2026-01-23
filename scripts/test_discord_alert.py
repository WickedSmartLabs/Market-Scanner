from scanner.alerts.discord import send_alert

send_alert({
    "status": "This is important",
    "symbol": "TEST/USD",
    "timeframe": "1m",
    "direction": "Up",
    "market_activity": "Quiet",
    "confidence": 9,
})
