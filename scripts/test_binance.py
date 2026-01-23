from scanner.connectors.binance.crypto import fetch_klines

if __name__ == "__main__":
    candles = fetch_klines("BTCUSDT", interval="1m", limit=20)
    print(f"Got {len(candles)} Binance candles.")
    print("First:", candles[0] if candles else None)
    print("Last :", candles[-1] if candles else None)
