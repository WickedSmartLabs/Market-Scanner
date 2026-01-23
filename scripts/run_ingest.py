from scanner.config.watchlist import WATCHLIST
from scanner.ingestion.ingest_polygon_stocks import ingest_symbol
from scanner.ingestion.ingest_coinbase_crypto import ingest_product


def run_ingest():
    for asset_class, items in WATCHLIST.items():
        for item in items:
            symbol = item["symbol"]

            if asset_class == "crypto":
                product = symbol.replace("/", "-")
                ingest_product(product)

            elif asset_class == "stock":
                ingest_symbol(symbol)


if __name__ == "__main__":
    run_ingest()
