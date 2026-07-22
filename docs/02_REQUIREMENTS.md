# AI Investment Manager
# Software Requirements Specification (SRS)

Version: 1.0

Status: Draft

Author: Muhammad Tariq Khan

---

# 1. Introduction

This document defines the complete functional and non-functional requirements of the AI Investment Manager.

All implementation decisions must trace back to requirements defined here.

---

# 2. Scope

The system shall provide an AI-powered investment advisory platform focused on wealth creation for Pakistani investors.

The initial version shall support:

- Mutual Funds
- Pakistan Stock Exchange (PSX)
- Portfolio Tracking
- AI Recommendations
- Portfolio Optimization
- Learning Engine
- Reporting
- Notifications

Future versions shall extend functionality without major architectural redesign.

---

# 3. Business Objectives

The platform shall:

• Maximize long-term portfolio value

• Improve investment decisions

• Reduce emotional investing

• Continuously improve recommendations

• Maintain explainability

• Remain extensible

---

# 4. User Profile

Current Target User

Country

Pakistan

Investment Style

Aggressive

Risk Profile

High

Investment Preference

Shariah Compliant

Primary Asset

Mutual Funds

Secondary Asset

Stocks

Monthly Investment

Configurable

Default

PKR 50,000

---

# 5. Functional Requirements

Each requirement shall have a unique identifier.

Priority Levels

M = Must

S = Should

C = Could

-----------------------------------------

## Portfolio Management

FR-001 (M)

The system shall maintain the complete investment portfolio.

FR-002 (M)

The system shall support manual portfolio updates.

FR-003 (M)

The system shall attempt automatic portfolio synchronization whenever supported.

FR-004 (M)

If synchronization is unavailable, the system shall request only the required numeric values.

Example:

AMMF

MEF

MGF

...

The user should only enter numbers.

FR-005 (M)

Historical portfolio snapshots shall be retained.

FR-006 (M)

Every investment transaction shall be stored.

FR-007 (M)

Every redemption shall be stored.

FR-008 (M)

Every fund switch shall be stored.

FR-009 (M)

Support investment notes.

FR-010 (S)

Support transaction attachments.

-----------------------------------------

## Mutual Fund Module

FR-020 (M)

Download all supported Shariah-compliant mutual funds.

FR-021 (M)

Store historical NAV.

FR-022 (M)

Track AUM.

FR-023 (M)

Track Expense Ratio.

FR-024 (M)

Track Fund Manager.

FR-025 (M)

Track Category.

FR-026 (M)

Track Sector Allocation.

FR-027 (M)

Track Top Holdings.

FR-028 (M)

Track Cash Allocation.

FR-029 (M)

Calculate rolling returns.

FR-030 (M)

Calculate CAGR.

FR-031 (M)

Calculate XIRR.

FR-032 (M)

Calculate Sharpe Ratio.

FR-033 (M)

Calculate Sortino Ratio.

FR-034 (M)

Calculate Alpha.

FR-035 (M)

Calculate Beta.

FR-036 (M)

Calculate Standard Deviation.

FR-037 (M)

Calculate Maximum Drawdown.

FR-038 (M)

Rank funds.

FR-039 (M)

Predict future performance.

FR-040 (M)

Recommend:

BUY

HOLD

SWITCH

SELL

WAIT

-----------------------------------------

## Stock Module

FR-050 (M)

Support PSX.

FR-051 (M)

Only recommend Shariah-compliant stocks.

FR-052 (M)

Collect company fundamentals.

FR-053 (M)

Collect technical indicators.

FR-054 (M)

Collect valuation metrics.

FR-055 (M)

Calculate momentum.

FR-056 (M)

Rank stocks.

FR-057 (M)

Predict expected return.

FR-058 (M)

Estimate downside risk.

FR-059 (S)

Recommend portfolio allocation.

-----------------------------------------

## Macroeconomic Engine

FR-070 (M)

Track SBP policy rate.

FR-071 (M)

Track CPI.

FR-072 (M)

Track PKR/USD.

FR-073 (M)

Track Gold.

FR-074 (M)

Track Oil.

FR-075 (M)

Track IMF developments.

FR-076 (M)

Track Budget announcements.

FR-077 (M)

Generate macroeconomic score.

-----------------------------------------

## News Engine

FR-090 (M)

Collect financial news.

FR-091 (M)

Remove duplicates.

FR-092 (M)

Cluster related articles.

FR-093 (M)

Perform sentiment analysis.

FR-094 (M)

Estimate sector impact.

FR-095 (M)

Estimate portfolio impact.

-----------------------------------------

## Prediction Engine

FR-110 (M)

Support ensemble prediction.

FR-111 (M)

Estimate expected return.

FR-112 (M)

Estimate volatility.

FR-113 (M)

Estimate confidence.

FR-114 (M)

Generate prediction explanations.

-----------------------------------------

## Portfolio Optimizer

FR-130 (M)

Optimize allocation.

FR-131 (M)

Respect diversification limits.

FR-132 (M)

Respect risk profile.

FR-133 (M)

Estimate efficient allocation.

FR-134 (S)

Support Modern Portfolio Theory.

FR-135 (C)

Support Black-Litterman.

FR-136 (C)

Support Risk Parity.

-----------------------------------------

## Recommendation Engine

FR-150 (M)

Generate only one primary recommendation.

Possible outputs:

DO NOTHING

BUY

SELL

SWITCH

WAIT

INVEST MONTHLY SIP

BUY STOCKS

REDUCE EQUITY

INCREASE EQUITY

FR-151 (M)

Every recommendation shall include:

Confidence

Reason

Supporting evidence

Expected return

Expected downside

Risk level

FR-152 (M)

Recommendations shall be explainable.

FR-153 (M)

Recommendations shall cite supporting indicators.

-----------------------------------------

## Learning Engine

FR-170 (M)

Store every recommendation.

FR-171 (M)

Store portfolio state.

FR-172 (M)

Track user response.

FR-173 (M)

Track actual outcome.

FR-174 (M)

Calculate prediction error.

FR-175 (M)

Compare prediction versus reality.

FR-176 (M)

Update model weights.

FR-177 (S)

Support automatic retraining.

FR-178 (S)

Support A/B testing.

FR-179 (M)

Generate self-evaluation reports.

-----------------------------------------

## Reporting

FR-190 (M)

Generate daily report.

FR-191 (M)

Generate weekly report.

FR-192 (M)

Generate monthly report.

FR-193 (M)

Generate yearly report.

FR-194 (M)

Support Markdown.

FR-195 (M)

Support HTML.

FR-196 (S)

Support PDF.

-----------------------------------------

## Notification Engine

FR-210 (M)

Support console notifications.

FR-211 (M)

Support email.

FR-212 (S)

Support Telegram.

FR-213 (S)

Support WhatsApp.

FR-214 (S)

Support Push Notifications.

Notification providers shall be replaceable.

-----------------------------------------

## Dashboard

FR-230 (S)

Provide web dashboard.

FR-231 (S)

Portfolio allocation.

FR-232 (S)

Performance charts.

FR-233 (S)

Recommendation history.

FR-234 (S)

Learning history.

FR-235 (S)

Risk dashboard.

-----------------------------------------

## API

FR-250 (S)

REST API.

FR-251 (C)

GraphQL.

FR-252 (C)

Public SDK.

-----------------------------------------

# 6. Non-Functional Requirements

NFR-001

System shall be modular.

NFR-002

System shall be testable.

NFR-003

System shall support dependency injection.

NFR-004

System shall follow SOLID principles.

NFR-005

System shall use type hints.

NFR-006

System shall support unit testing.

NFR-007

System shall support integration testing.

NFR-008

System shall support logging.

NFR-009

System shall degrade gracefully when external data is unavailable.

NFR-010

No business logic shall depend on a single external provider.

NFR-011

Every external integration shall be abstracted behind interfaces.

NFR-012

The system shall remain extensible without significant refactoring.

---

# 7. Business Rules

BR-001

Never recommend non-Shariah-compliant investments unless explicitly enabled.

BR-002

Never recommend actions without supporting evidence.

BR-003

Never recommend daily switching based solely on NAV changes.

BR-004

Confidence must be calibrated.

BR-005

Do Nothing is a valid recommendation.

BR-006

All recommendations shall be reproducible.

BR-007

Every recommendation shall be stored.

BR-008

Every recommendation shall later be evaluated.

---

# 8. Assumptions

- External financial data sources remain available.
- Historical market data can be stored locally.
- Users provide accurate portfolio information when automatic synchronization is unavailable.
- Recommendations remain advisory; investment decisions are ultimately made by the user.

---

# 9. Constraints

- Pakistani market focus in initial releases.
- Shariah-compliant investments only.
- Python-first implementation.
- Open architecture allowing additional data providers and investment products.

---

# 10. Acceptance Criteria

The system shall be considered production-ready when it can:

- Maintain an accurate portfolio.
- Collect and normalize investment data.
- Analyze mutual funds and PSX stocks.
- Produce explainable recommendations.
- Learn from historical outcomes.
- Generate scheduled reports.
- Notify the user through supported channels.
- Continue operating gracefully when one or more data sources are unavailable.
- Be extended with new providers or investment products without major architectural changes.

---

# End of Document