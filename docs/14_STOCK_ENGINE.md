# AI Investment Manager
# Stock Engine

Version: 1.0

Status: MVP

---

# 1. Purpose

The Stock Engine is responsible for collecting, analyzing, evaluating and ranking Pakistan Stock Exchange (PSX) listed companies.

It provides the AI Decision Engine with stock insights, technical indicators, valuation metrics and investment opportunities.

The primary goal is to identify high-quality stocks capable of outperforming mutual funds while remaining suitable for the user's investment profile.

---

# 2. Responsibilities

The Stock Engine shall

- Import stock prices
- Maintain company master data
- Track historical prices
- Calculate technical indicators
- Calculate financial ratios
- Analyze sectors
- Rank companies
- Detect opportunities
- Generate AI Scores
- Recommend stocks

---

# 3. Supported Markets

Current

- Pakistan Stock Exchange (PSX)

Future

- US Stocks
- GCC Markets
- ETFs
- REITs

---

# 4. Company Master

Maintain information for every listed company.

Fields

- Company Name
- Symbol
- Sector
- Industry
- Market
- Listing Date
- Market Capitalization
- Free Float
- Shariah Status
- Website

---

# 5. Historical Prices

Maintain complete history.

Fields

- Symbol
- Date
- Open
- High
- Low
- Close
- Volume
- Adjusted Close
- Source

Historical records are immutable.

---

# 6. Fundamental Metrics

Track

- EPS
- PE Ratio
- PB Ratio
- Dividend Yield
- ROE
- ROA
- Debt to Equity
- Earnings Growth
- Revenue Growth
- Market Capitalization

---

# 7. Technical Indicators

Calculate

- SMA
- EMA
- RSI
- MACD
- Bollinger Bands
- ATR
- ADX
- Volume Trend
- Momentum

Indicators should be recalculated automatically.

---

# 8. Performance Metrics

Calculate

- Daily Return
- Weekly Return
- Monthly Return
- Quarterly Return
- Annual Return
- CAGR
- Volatility
- Maximum Drawdown

---

# 9. Sector Analysis

Analyze

- Sector Performance
- Sector Rotation
- Sector Strength
- Sector Momentum
- Sector Ranking

Examples

- Banking
- Cement
- Fertilizer
- Oil & Gas
- Technology
- Power
- Pharmaceuticals

---

# 10. Stock Ranking

Generate rankings using

- Historical Performance
- Momentum
- Fundamentals
- Technical Indicators
- Risk
- Liquidity
- AI Score

---

# 11. AI Stock Score

Each stock receives an AI Score (0–100).

Factors

- Growth
- Value
- Momentum
- Financial Health
- Technical Strength
- Sector Strength
- Market Regime
- News Sentiment

Scores are recalculated automatically.

---

# 12. Buy Opportunity Detection

Identify opportunities such as

- Breakout
- Trend Reversal
- Oversold Conditions
- High Growth Potential
- Undervalued Stocks

Recommendations include

- Confidence
- Expected Return
- Risk Level
- Suggested Holding Period

---

# 13. Portfolio Exposure

Calculate exposure by

- Company
- Sector
- Industry
- Market Cap
- Risk Level

Warn when concentration exceeds configured thresholds.

---

# 14. Market Regime Awareness

Recommendations should adapt to market conditions.

Examples

Bull Market

- Favor growth stocks

Bear Market

- Favor defensive sectors

High Inflation

- Reduce vulnerable sectors

Low Interest Rates

- Favor growth-oriented sectors

---

# 15. Shariah Compliance

Track

- Shariah Status
- Compliance Source
- Last Review Date

If Shariah Mode is enabled,

only compliant companies may be recommended.

---

# 16. Integration

Consumes

- Historical Prices
- Financial Data
- Market Intelligence
- News
- AI Decision Engine

Provides

- Rankings
- Technical Analysis
- AI Scores
- Buy Opportunities
- Sector Analysis

---

# 17. Public Services

The module shall expose

- Get Company Details
- Get Historical Prices
- Calculate Indicators
- Calculate Fundamentals
- Generate Rankings
- Calculate AI Score
- Detect Buy Opportunities

---

# 18. API Requirements

Minimum endpoints

GET /stocks

GET /stocks/{symbol}

GET /stocks/history

GET /stocks/rankings

GET /stocks/sectors

GET /stocks/compare

GET /stocks/opportunities

---

# 19. Business Rules

- Historical prices are immutable.
- Indicators are recalculated after every price update.
- Recommendations must include confidence scores.
- Only Shariah-compliant stocks are recommended when enabled.
- Portfolio exposure limits must be respected.

---

# 20. Success Criteria

The Stock Engine is complete when

✓ Historical prices imported

✓ Technical indicators calculated

✓ Financial metrics available

✓ Sector analysis completed

✓ Rankings generated

✓ AI Scores calculated

✓ Buy opportunities detected

✓ AI Decision Engine consumes stock insights

---

# End of 14_STOCK_ENGINE.md