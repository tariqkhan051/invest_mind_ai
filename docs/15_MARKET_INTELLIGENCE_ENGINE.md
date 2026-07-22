# AI Investment Manager
# Market Intelligence Engine

Version: 1.0

Status: MVP

---

# 1. Purpose

The Market Intelligence Engine collects, analyzes and interprets external market information that influences investment decisions.

Unlike the Mutual Fund and Stock Engines, this module focuses on the broader market environment rather than individual assets.

It provides economic context, sentiment analysis and market regime detection for the AI Decision Engine.

---

# 2. Responsibilities

The Market Intelligence Engine shall

- Collect economic indicators
- Monitor market news
- Analyze sentiment
- Track interest rates
- Monitor inflation
- Monitor exchange rates
- Monitor commodity prices
- Detect market regimes
- Generate market scores
- Provide investment signals

---

# 3. Data Sources

Current

- State Bank of Pakistan (SBP)
- Pakistan Bureau of Statistics (PBS)
- PSX
- RSS News Feeds
- Public Financial APIs

Future

- Trading Economics
- Bloomberg
- Reuters
- IMF
- World Bank
- Alpha Vantage

---

# 4. Macroeconomic Indicators

Track

- Inflation (CPI)
- Policy Interest Rate
- USD/PKR Exchange Rate
- Foreign Exchange Reserves
- GDP Growth
- Fiscal Deficit
- Current Account
- Oil Prices
- Gold Prices

Each indicator shall maintain complete historical records.

---

# 5. News Collection

Collect news related to

- Pakistan Economy
- PSX
- Mutual Funds
- Asset Management Companies
- Listed Companies
- Banking Sector
- Government Policies
- Global Events affecting Pakistan

Each article shall include

- Title
- Source
- Publication Time
- URL
- Summary
- Category

---

# 6. News Classification

Automatically classify news into categories

- Economy
- Politics
- Banking
- Energy
- Technology
- Corporate Earnings
- Regulations
- Global Markets
- Mutual Funds

Multiple categories may apply.

---

# 7. Sentiment Analysis

Assign sentiment to each news item

- Positive
- Neutral
- Negative

Also calculate

- Confidence Score
- Sentiment Strength

Future versions may use LLM-based sentiment analysis.

---

# 8. Market Regime Detection

Determine the current market regime.

Supported regimes

- Strong Bull
- Bull
- Neutral
- Bear
- Strong Bear
- High Inflation
- High Interest Rate
- Recovery
- Volatile Market

The AI Decision Engine uses this regime to adjust recommendations.

---

# 9. Economic Calendar

Track important events

Examples

- Monetary Policy Announcements
- Federal Budget
- Inflation Releases
- GDP Reports
- Corporate Earnings
- PSX Holidays

Events may affect AI confidence.

---

# 10. Market Score

Generate a Market Intelligence Score (0–100).

Factors

- Economic Indicators
- Market Trend
- News Sentiment
- Interest Rate Direction
- Inflation Trend
- Currency Stability
- Global Risk

The score summarizes the overall investment environment.

---

# 11. Investment Signals

Generate signals such as

- Increase Equity Exposure
- Increase Money Market Allocation
- Increase Income Fund Allocation
- Hold Cash
- Reduce Risk
- Favor Defensive Sectors
- Favor Growth Sectors

Signals are advisory and consumed by the AI Decision Engine.

---

# 12. Alerts

Generate alerts for

- Interest Rate Changes
- Inflation Surprises
- Significant Currency Movements
- Major Political Events
- Market Crashes
- Exceptional Bull Runs

Alerts should include severity and potential portfolio impact.

---

# 13. Integration

Consumes

- Economic Data
- News Sources
- Market Prices

Provides

- Market Regime
- Sentiment Scores
- Market Score
- Investment Signals
- Alerts

---

# 14. Public Services

The module shall expose

- Get Market Summary
- Get Latest News
- Get Economic Indicators
- Get Market Regime
- Get Sentiment Analysis
- Get Market Score
- Get Investment Signals

---

# 15. API Requirements

Minimum endpoints

GET /market/summary

GET /market/news

GET /market/news/{id}

GET /market/economy

GET /market/regime

GET /market/signals

GET /market/score

GET /market/alerts

---

# 16. Business Rules

- Historical economic data is immutable.
- Duplicate news items shall not be stored.
- Market regime shall be recalculated whenever significant new data is received.
- Sentiment analysis shall be repeatable and versioned.
- Market scores shall be explainable.

---

# 17. Success Criteria

The Market Intelligence Engine is complete when

✓ Economic indicators collected

✓ News imported

✓ Sentiment analyzed

✓ Market regime detected

✓ Market score calculated

✓ Investment signals generated

✓ Alerts available

✓ AI Decision Engine consumes market intelligence

---

# End of 15_MARKET_INTELLIGENCE_ENGINE.md