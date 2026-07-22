# AI Investment Manager
# AI Decision Engine

Version: 1.0

Status: MVP

---

# 1. Purpose

The AI Decision Engine is the central intelligence module of the AI Investment Manager.

Its purpose is to transform market data, portfolio information and economic conditions into clear, explainable and actionable investment recommendations.

The engine acts as a financial advisor, not an autonomous trading system.

Final investment decisions always remain with the user.

---

# 2. Responsibilities

The AI Decision Engine shall

- Analyze portfolio
- Analyze mutual funds
- Analyze stocks
- Analyze market conditions
- Evaluate risk
- Predict opportunities
- Recommend investments
- Recommend fund switches
- Recommend redemptions
- Recommend holding cash
- Learn from previous outcomes

---

# 3. Inputs

The engine consumes data from

Portfolio Engine

Mutual Fund Engine

Stock Engine

Market Intelligence Engine

Historical Performance

User Preferences

Learning History

Investment Goals

Risk Profile

Monthly Investment Budget

---

# 4. Daily Decision Flow

Every execution follows the same workflow.

Collect Latest Data

↓

Update Portfolio

↓

Analyze Market

↓

Analyze Mutual Funds

↓

Analyze Stocks

↓

Evaluate Risk

↓

Generate Opportunities

↓

Rank Opportunities

↓

Generate Recommendations

↓

Generate Explanation

↓

Store Results

---

# 5. Possible Recommendations

The engine may recommend

- Do Nothing
- Invest Monthly Amount
- Invest Additional Cash
- Switch Funds
- Redeem Fund
- Buy Stock
- Sell Stock
- Increase Cash Allocation
- Wait for Better Opportunity

Every recommendation must include a reason.

---

# 6. Decision Priorities

The engine evaluates opportunities in this order

1. Portfolio Risk
2. Capital Preservation
3. Monthly Investment
4. Fund Switching
5. New Mutual Fund Investment
6. Direct Stock Investment
7. Cash Position

Higher priority rules override lower priority recommendations.

---

# 7. Recommendation Object

Every recommendation contains

- Recommendation ID
- Date
- Action
- Asset
- Amount
- Confidence Score
- Expected Return
- Risk Level
- Holding Period
- Explanation
- Supporting Evidence

Example

Action

Switch

From

AMMF

To

MEF

Amount

250,000 PKR

Confidence

87%

Reason

Strong equity momentum while money market outlook weak.

---

# 8. Opportunity Scoring

Every opportunity receives a score (0–100).

Factors include

- Expected Return
- Historical Performance
- Momentum
- Market Regime
- Risk
- Diversification Benefit
- Liquidity
- Fund Quality
- News Sentiment

Only top-ranked opportunities become recommendations.

---

# 9. Mutual Fund Decision Rules

Evaluate

Performance

Momentum

Risk

Market Regime

NAV Trend

Switch Cost

Portfolio Allocation

Possible actions

Buy

Increase

Reduce

Switch

Redeem

Hold

---

# 10. Stock Decision Rules

Evaluate

Technical Indicators

Fundamentals

Sector Strength

Market Regime

Liquidity

Shariah Compliance

Possible actions

Buy

Increase

Reduce

Sell

Hold

---

# 11. Portfolio Optimization

Goals

Maximize long-term returns

Maintain diversification

Respect risk limits

Maintain liquidity

Respect Shariah compliance

The optimizer recommends target allocations rather than individual trades alone.

---

# 12. Risk Evaluation

Evaluate

Portfolio Concentration

Sector Concentration

Fund Concentration

Volatility

Liquidity

Cash Allocation

Market Conditions

Generate

Risk Score

Risk Level

Warnings

---

# 13. Confidence Score

Every recommendation includes confidence.

Inputs

Historical Accuracy

Market Stability

Model Agreement

Data Quality

Learning History

Recent Prediction Performance

Range

0–100%

Recommendations below the configured minimum confidence should not be shown.

---

# 14. Explainability

Every recommendation must answer

Why?

Why now?

Why this investment?

Why not another option?

Expected benefit?

Possible risks?

No recommendation should appear without an explanation.

---

# 15. Learning

The engine records

Recommendation

↓

User Action

↓

Market Outcome

↓

Prediction Accuracy

↓

Reward

↓

Knowledge Update

↓

Future Improvement

Learning is continuous.

---

# 16. User Feedback

The user may

Accept Recommendation

Reject Recommendation

Modify Amount

Ignore Recommendation

Request Explanation

Feedback becomes part of future decision making.

---

# 17. Business Rules

- Never recommend non-Shariah investments when Shariah Mode is enabled.
- Never exceed configured risk limits.
- Never recommend investments without supporting data.
- Every recommendation must be explainable.
- Every recommendation is stored for future evaluation.

---

# 18. Public Services

The module shall expose

Generate Recommendations

Evaluate Portfolio

Calculate Opportunity Scores

Optimize Allocation

Calculate Confidence

Generate Explanation

Record Feedback

Run Learning Cycle

---

# 19. API Requirements

Minimum endpoints

GET /recommendations

GET /recommendations/latest

GET /recommendations/history

POST /recommendations/feedback

GET /recommendations/explanation/{id}

POST /recommendations/run

---

# 20. Success Criteria

The AI Decision Engine is complete when

✓ Portfolio analyzed

✓ Market analyzed

✓ Opportunities ranked

✓ Recommendations generated

✓ Confidence calculated

✓ Explanations generated

✓ User feedback captured

✓ Learning updated

---

# Appendix A – Example Daily Output

Date

09 July 2026

Recommendation

Invest PKR 50,000 into Meezan Islamic Fund (MIF)

Confidence

91%

Reason

- Equity market in Bull regime
- MIF momentum exceeds category average
- Portfolio currently underweight in equity
- Inflation expected to ease
- Risk remains within configured limits

Alternative

Switch PKR 100,000 from AMMF to MEF

Confidence

84%

If No Action Is Recommended

Recommendation

No Action Today

Reason

- Portfolio allocation remains optimal
- No high-conviction opportunities identified
- Market uncertainty elevated
- Preserve cash until stronger signals emerge

---

# End of 16_AI_DECISION_ENGINE.md