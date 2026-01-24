# Market Scanner

A production-style market analysis and research system for studying short-term trading setups in stocks and crypto using disciplined, probability-based logic.

This project focuses on **signal quality, market context, and risk awareness**, not trade automation or prediction.

---

## Overview

**Market Scanner** is a personal research platform designed to answer one question:

> *Is this market state worth paying attention to right now?*

The system continuously ingests market data, analyzes price structure, scores setup quality, and logs results for later evaluation.  
It is intentionally **human-in-the-loop** — providing context, not commands.

---

## Key Characteristics

- Not an auto-trading bot
- No buy/sell signals
- Rule-based and explainable logic
- Persistent historical analysis
- Designed for learning and evidence-building

---

## What the System Analyzes

For each symbol and timeframe, the scanner evaluates:

- **Trend direction** (up, down, sideways)
- **Volatility regime** (quiet, normal, active)
- **Pause / consolidation detection**
- **Volume confirmation**
- **ATR (Average True Range)** for reference risk sizing
- **Price snapshot** at detection time

All results are scored and logged for later outcome analysis.

---

## Confidence Scoring

Each setup is assigned a **confidence score from 0 to 10**, based on rule-based criteria:

- Trend clarity
- Consolidation quality
- Volatility context
- Volume confirmation

Scores are capped intentionally to avoid false precision.

---

## Status Labels

The scanner uses simple, human-readable status labels:

| Status | Meaning |
|------|--------|
| Low priority | Market noise or unclear structure |
| Getting interesting | Worth monitoring |
| This is important | High-quality setup requiring review |

These represent **attention levels**, not trade instructions.

---

## Research Universe

The universe is intentionally small and controlled to allow clean analysis.

### Stocks
- **SPY** — market regime proxy
- **AAPL**
- **MSFT**

### Crypto
- **BTC/USD** — primary market driver
- **ETH/USD**
- **SOL/USD** — risk-on leader

---

## System Architecture
Market APIs (Polygon, Coinbase)
        ↓
Data Ingestion (scheduled, idempotent)
        ↓
PostgreSQL (candles and analysis history)
        ↓
Market Analysis (trend, volatility, pause detection)
        ↓
Rule-Based Scoring (0–10 confidence)
        ↓
Outputs (terminal, database, alert-ready)


---

## Technology Stack

- Python 3
- PostgreSQL
- SQLAlchemy
- Docker / Docker Compose
- Cron scheduling
- Polygon.io (stocks)
- Coinbase API (crypto)

---

## Project Structure
     src/
      scanner/  
        analysis/        # market logic
        features/        # indicators (ATR, volume, pauses)
        ingestion/       # API ingestion
        storage/         # database models and sessions
        config/          # watchlist and settings  

    scripts/
      run_ingest.py
      run_scan.py
      run_pipeline.py

    logs/
      pipeline.log


---

## How It Runs

- Ingestion and analysis run every five minutes
- Managed via cron
- Results are:
  - Printed to the terminal
  - Stored in PostgreSQL
  - Ready for alerts or dashboards

Once configured, the system runs unattended.

---

## Example Output
    SCAN COMPLETE - 6 symbols analyzed

    GETTING INTERESTING
    BTC/USD | Down | Confidence: 6/10 | $89,430
    ETH/USD | Down | Confidence: 5/10 | $2,935

    LOW PRIORITY: 4 symbols


---

## Outcome Evaluation (Planned)

The database schema already supports:

- Forward return tracking
- Outcome labeling
- Performance analysis by confidence level

These features are intentionally deferred until sufficient real data accumulates.

---

## What This Project Is Not

- Not an automated trading system
- Not a prediction engine
- Not financial advice
- Not optimized for hype or overfitting

---

## Future Extensions

Planned, evidence-driven expansions:

- Outcome evaluation and expectancy metrics
- Interactive dashboard
- Options overlays (after underlying edge is proven)
- Universe expansion using liquidity and volatility filters

Machine learning will only be considered if rule-based methods plateau.

---

## About the Author

This project was built by a developer early in their journey into data engineering, market systems, and quantitative analysis.

The primary goal of this work is learning by building — designing a real, end-to-end system to better understand how market data flows, how trading setups can be evaluated objectively, and how disciplined research differs from speculation.

Rather than following tutorials or building one-off scripts, this project emphasizes:

  - Building production-style pipelines from scratch

  - Using real APIs, databases, and scheduling tools

  - Writing explainable, rule-based logic

  - Letting data accumulate before drawing conclusions

The system reflects an intentional focus on foundational skills, systems thinking, and responsible experimentation, with the expectation that both the codebase and the author’s understanding will continue to evolve over time.

---

## Disclaimer

This project is for educational and research purposes only.  
All trading decisions remain the responsibility of the user.
