# AI Investment Manager
# Mutual Fund Engine

Version: 1.0

Status: MVP

---

# 1. Purpose

The Mutual Fund Engine is responsible for analyzing, evaluating, comparing, and recommending mutual funds.

It provides the AI Decision Engine with detailed insights into fund performance, risk, diversification, and switching opportunities.

The engine focuses on long-term wealth creation while maintaining Shariah compliance.

---

# 2. Responsibilities

The Mutual Fund Engine shall:

- Import daily NAVs
- Maintain fund metadata
- Calculate returns
- Rank funds
- Compare funds
- Identify switching opportunities
- Calculate risk metrics
- Monitor portfolio exposure
- Detect trends
- Generate fund scores

---

# 3. Supported Fund Types

Current

- Money Market Fund
- Income Fund
- Islamic Income Fund
- Equity Fund
- Islamic Equity Fund
- Asset Allocation Fund
- Balanced Fund
- Cash Fund
- Index Fund

Future

- ETF
- International Funds
- Pension Funds

---

# 4. Fund Master

Maintain master information for every fund.

Fields

- Fund Name
- AMC
- Fund Category
- Shariah Status
- Launch Date
- Benchmark
- Currency
- Management Fee
- Front Load
- Back Load
- Risk Category
- Minimum Investment
- Dividend Policy
- Fund Size (AUM)

---

# 5. NAV History

Maintain complete historical NAV.

Each record contains

- Fund
- NAV Date
- NAV
- Daily Change
- Daily Return
- Source
- Import Time

Historical NAV must never be modified.

---

# 6. Performance Metrics

Calculate

- Daily Return
- Weekly Return
- Monthly Return
- Quarterly Return
- Yearly Return
- 3-Year CAGR
- 5-Year CAGR
- Since Inception Return

---

# 7. Risk Metrics

Calculate

- Volatility
- Standard Deviation
- Maximum Drawdown
- Sharpe Ratio (future)
- Sortino Ratio (future)
- Downside Risk
- Recovery Time

---

# 8. Fund Rankings

Generate rankings by

- Daily Performance
- Monthly Performance
- Annual Return
- CAGR
- Risk
- AUM
- Consistency
- AI Score

Rankings should be updated automatically.

---

# 9. Fund Comparison

Support comparison of multiple funds.

Compare

- Returns
- Risk
- Fees
- NAV Growth
- Drawdown
- AUM
- Dividend History
- Expense Ratio

---

# 10. AI Fund Score

Every fund receives an AI Score (0–100).

Factors

- Historical Performance
- Momentum
- Volatility
- Consistency
- Liquidity
- Fund Size
- Category Strength
- Market Conditions
- News Sentiment

The AI Score is one input to recommendations.

---

# 11. Switching Analysis

Identify opportunities to switch between funds.

Examples

Money Market → Equity Fund

Income Fund → Equity Fund

Equity Fund → Money Market

Switch recommendations must consider

- Expected Return
- Risk
- Market Regime
- User Profile
- Holding Period

---

# 12. Category Analysis

Analyze fund categories.

Metrics

- Average Return
- Average Risk
- Best Performer
- Worst Performer
- Category Trend
- Momentum

---

# 13. Portfolio Exposure

Calculate exposure by

- AMC
- Fund Category
- Risk Level
- Asset Class

Warn when concentration exceeds configured thresholds.

---

# 14. Dividend Tracking

Track

- Dividend Date
- Dividend Amount
- Dividend Type
- Reinvestment
- Cash Distribution

Future

Dividend forecasting.

---

# 15. Market Regime Awareness

Adjust fund recommendations based on market conditions.

Examples

Bull Market

Prefer Equity Funds

Bear Market

Increase Money Market allocation

High Interest Rates

Prefer Income Funds

Low Interest Rates

Increase Growth allocation

---

# 16. Recommendation Rules

The engine may recommend

- Buy
- Increase Investment
- Reduce Investment
- Switch Funds
- Hold
- Exit Position

Every recommendation must include

- Reason
- Confidence
- Expected Benefit
- Risk Assessment

---

# 17. Integration

Consumes

- NAV History
- Portfolio
- Market Intelligence
- AI Decision Engine

Provides

- Fund Scores
- Rankings
- Risk Metrics
- Switch Opportunities
- Comparison Results

---

# 18. Public Services

The module shall expose

- Get Fund Details
- Get NAV History
- Compare Funds
- Calculate Returns
- Calculate Risk
- Generate Rankings
- Detect Switch Opportunities
- Calculate AI Score

---

# 19. API Requirements

Minimum endpoints

GET /funds

GET /funds/{id}

GET /funds/nav-history

GET /funds/rankings

GET /funds/compare

GET /funds/categories

GET /funds/switch-opportunities

---

# 20. Success Criteria

The Mutual Fund Engine is complete when

✓ Daily NAVs imported

✓ Historical NAV maintained

✓ Performance calculated

✓ Risk metrics available

✓ Rankings generated

✓ AI Scores calculated

✓ Fund comparison available

✓ Switch opportunities identified

✓ AI Decision Engine consumes results

---

# End of 13_MUTUAL_FUND_ENGINE.md