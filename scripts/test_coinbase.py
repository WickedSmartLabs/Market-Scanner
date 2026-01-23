from scanner.connectors.coinbase.crypto import fetch_candles

if __name__ == "__main__":
    candles = fetch_candles("BTC-USD", granularity=60, limit=20)
    print(f"Got {len(candles)} Coinbase candles.")
    print("First:", candles[0] if candles else None)
    print("Last :", candles[-1] if candles else None)
