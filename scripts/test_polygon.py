from scanner.connectors.polygon.stocks import fetch_daily_aggregates

if __name__ == "__main__":
    candles = fetch_daily_aggregates("AAPL", limit=20)
    print(f"Got {len(candles)} Polygon DAILY candles.")
    print("First:", candles[0] if candles else None)
    print("Last :", candles[-1] if candles else None)
