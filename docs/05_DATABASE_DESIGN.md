# AI Investment Manager
# Database Design

Version: 1.0

Status: Draft

---

# 1. Purpose

This document defines the physical persistence architecture for the AI Investment Manager.

It transforms the Domain Model into a relational database structure while preserving:

- Domain boundaries
- Aggregate ownership
- Data consistency
- Auditability
- Historical accuracy
- Scalability
- Performance

The database is designed to support:

- Local development (SQLite)
- Production deployment (PostgreSQL)
- Future horizontal scaling

---

# 2. Design Principles

The database follows these principles.

## Business First

Tables exist because of business concepts.

Not the other way around.

Every table originates from an Aggregate or Entity defined in the Domain Model.

---

## Historical Accuracy

Financial systems never rewrite history.

Historical data is immutable.

Examples

Transactions

NAV History

Price History

Predictions

Recommendations

Learning Records

Snapshots

must never be updated after confirmation.

---

## Auditability

Every important business operation should be reproducible.

The database must always answer:

Who changed this?

When?

Why?

Using which model?

Using which strategy?

---

## Separation of Concerns

Operational data

↓

Analytical data

↓

Reporting data

↓

Machine Learning data

should remain logically separated.

---

## Explainability

Every recommendation must be traceable to:

Portfolio

↓

Market Data

↓

Features

↓

Prediction

↓

Decision

↓

Recommendation

↓

Learning Outcome

---

## PostgreSQL First

Production database:

PostgreSQL

Development database:

SQLite

No vendor-specific SQL should leak into business logic.

---

# 3. Database Architecture

The platform follows a layered persistence architecture.

```

Application

↓

Domain

↓

Repository

↓

ORM

↓

Database

```

The Domain Layer never communicates directly with SQL.

Repositories abstract persistence.

---

# 4. Database Type

Relational Database

Primary

PostgreSQL

Secondary

SQLite

Future Support

DuckDB (Analytics)

ClickHouse (Large-scale reporting)

TimescaleDB (Time-series optimization)

---

# 5. Database Modules

The database is divided into business modules.

Portfolio

Asset

Market

AI

Learning

Reporting

Notifications

Configuration

System

Each module owns its tables.

---

# 6. Schema Organization

Logical organization.

public

├── portfolio

├── asset

├── market

├── ai

├── learning

├── reporting

├── notification

├── configuration

└── system

SQLite will emulate schemas using table prefixes.

Example

portfolio_holdings

portfolio_transactions

asset_funds

asset_stocks

market_news

market_macro

---

# 7. Naming Standards

Tables

snake_case

Singular business meaning

Examples

portfolio

holding

transaction

recommendation

prediction

strategy

backtest

---

Columns

snake_case

Examples

portfolio_id

asset_id

created_at

updated_at

risk_score

confidence

---

Primary Keys

Always

id

UUID

---

Foreign Keys

Referenced object

portfolio_id

asset_id

holding_id

prediction_id

---

Booleans

is_active

is_deleted

is_shariah

is_current

---

Timestamps

created_at

updated_at

deleted_at

executed_at

evaluated_at

---

# 8. Identifier Strategy

Every aggregate uses UUID.

Advantages

Globally unique

Distributed-safe

No enumeration attacks

Supports offline creation

---

# 9. Soft Delete Policy

Business records are never physically deleted.

Instead

deleted_at

is_deleted

Examples

Portfolio

Recommendation

Report

User Configuration

Historical financial data

is never deleted.

---

# 10. Temporal Data

Time matters.

Historical information should be preserved.

Examples

NAV

Price

Predictions

Recommendations

Portfolio Snapshots

Macro Indicators

Market Regimes

Each record contains:

Effective Date

Created Date

Version

---

# 11. Versioning Strategy

Versioned tables include

Models

Strategies

Recommendations

Predictions

Policies

Configuration

Feature Sets

Versioning guarantees reproducibility.

---

# 12. Data Categories

Operational Data

Current Holdings

Current Portfolio

Current Allocation

---

Reference Data

Funds

Stocks

Categories

Sectors

Currencies

---

Historical Data

Transactions

NAV

Prices

Snapshots

Recommendations

Learning

---

Analytical Data

Feature Store

Backtests

Experiments

Statistics

---

Configuration Data

Strategies

Policies

System Settings

Providers

Notification Rules

---

# 13. Data Ownership

Every table has exactly one owner.

Portfolio Module

owns

Holdings

Transactions

Goals

Snapshots

Asset Module

owns

Funds

Stocks

NAV

Prices

Market Module

owns

News

Macro

Sentiment

Market Regimes

AI Module

owns

Predictions

Recommendations

Models

Learning Module

owns

Learning Records

Evaluation

Experiments

Ownership never overlaps.

---

# 14. Relationship Principles

Prefer

One-to-Many

over

Many-to-Many

When Many-to-Many is required

always use junction tables.

Example

Fund

↓

Fund Holdings

↓

Stock

---

# 15. Data Integrity

Constraints are preferred over application logic.

Examples

NOT NULL

CHECK

UNIQUE

FOREIGN KEY

Indexes

Composite Keys

Business validation remains in the Domain.

Database validation ensures consistency.

---

# 16. Scalability Strategy

Current Scale

One User

↓

Future

Multiple Users

↓

Thousands

↓

Enterprise

↓

Cloud

The schema should not require redesign.

---

# 17. Performance Principles

Normalize first.

Denormalize only when justified.

Use indexes.

Avoid duplicated data.

Materialize expensive calculations.

Use snapshots.

---

# 18. Financial Data Principles

Financial data must satisfy:

Immutability

Precision

Auditability

Repeatability

Reconciliation

Traceability

Consistency

No floating-point arithmetic for monetary values.

---

# 19. Security Principles

Sensitive data encrypted where appropriate.

Least privilege.

Read-only analytical users.

Audit logging.

Migration history.

No secrets inside the database.

---

# 20. Success Criteria

The database is considered successful when:

Every Aggregate maps naturally to tables.

Historical information is preserved.

Queries remain performant.

Business rules are enforceable.

Future expansion requires minimal schema changes.

Production and development remain compatible.

---

# End of Part 1

# AI Investment Manager
# Database Design
# Part 2 – Portfolio Schema

---

# 21. Portfolio Module Overview

The Portfolio module is responsible for storing the user's investment portfolio.

It owns:

Portfolio

Holding

Transaction

Portfolio Snapshot

Investment Goal

Cash Flow

Portfolio Metrics

Portfolio Allocation

The Portfolio module never stores market data.

It references Assets managed by the Asset Module.

---

# 22. Portfolio Table

Purpose

Represents one investment portfolio.

Table

portfolio

Primary Key

id (UUID)

Columns

id

owner_id

name

description

base_currency

risk_profile

investment_preference

investment_objective

investment_horizon

monthly_sip

status

version

created_at

updated_at

deleted_at

Indexes

PK(id)

IDX(owner_id)

IDX(status)

Unique Constraints

(owner_id, name)

Relationships

Portfolio

↓

Holdings

↓

Transactions

↓

Snapshots

↓

Goals

---

# 23. Holding Table

Purpose

Represents current ownership of one asset.

Table

holding

Primary Key

id

Columns

id

portfolio_id

asset_id

asset_type

quantity

average_cost

current_price

current_value

cost_basis

unrealized_gain

realized_gain

allocation_percentage

currency

status

last_price_update

created_at

updated_at

Indexes

PK(id)

IDX(portfolio_id)

IDX(asset_id)

IDX(status)

Unique

(portfolio_id, asset_id)

Foreign Keys

portfolio_id → portfolio.id

asset_id → asset.id

Business Rules

Only one active holding per asset.

Closed holdings remain.

---

# 24. Transaction Table

Purpose

Stores immutable investment transactions.

Table

transaction

Primary Key

id

Columns

id

portfolio_id

holding_id

asset_id

transaction_type

units

price

gross_amount

fees

taxes

net_amount

reference_number

transaction_date

settlement_date

notes

source

status

created_at

Indexes

PK(id)

IDX(portfolio_id)

IDX(asset_id)

IDX(transaction_date)

IDX(status)

Foreign Keys

portfolio_id

holding_id

asset_id

Rules

Immutable after confirmation.

---

# 25. Portfolio Snapshot Table

Purpose

Captures historical portfolio state.

Table

portfolio_snapshot

Columns

id

portfolio_id

snapshot_date

total_value

investment_value

cash_value

daily_return

monthly_return

yearly_return

xirr

cagr

volatility

drawdown

sharpe_ratio

sortino_ratio

allocation_json

sector_allocation_json

notes

created_at

Indexes

IDX(portfolio_id)

IDX(snapshot_date)

Unique

(portfolio_id, snapshot_date)

Purpose

Historical reporting

Learning Engine

Performance

Backtesting

---

# 26. Investment Goal Table

Purpose

Stores financial goals.

Table

investment_goal

Columns

id

portfolio_id

name

target_amount

current_amount

target_date

monthly_contribution

priority

risk_preference

status

notes

created_at

updated_at

Indexes

IDX(portfolio_id)

IDX(status)

---

# 27. Portfolio Cash Flow

Purpose

Supports XIRR calculations.

Table

portfolio_cashflow

Columns

id

portfolio_id

transaction_id

cashflow_date

cashflow_type

amount

currency

created_at

Indexes

IDX(portfolio_id)

IDX(cashflow_date)

Purpose

Cash flows are separated to simplify:

XIRR

CAGR

Forecasting

Learning

---

# 28. Portfolio Allocation History

Purpose

Historical allocation.

Table

portfolio_allocation_history

Columns

id

portfolio_id

snapshot_date

asset_type

sector

allocation_percentage

market_value

Indexes

IDX(portfolio_id)

IDX(snapshot_date)

Purpose

Track allocation changes.

---

# 29. Portfolio Metrics

Purpose

Stores expensive calculations.

Table

portfolio_metric

Columns

id

portfolio_id

calculation_date

portfolio_value

risk_score

expected_return

volatility

beta

alpha

treynor

information_ratio

max_drawdown

score

Indexes

IDX(portfolio_id)

IDX(calculation_date)

Purpose

Avoid recalculating expensive metrics.

---

# 30. Portfolio Notes

Purpose

User annotations.

Table

portfolio_note

Columns

id

portfolio_id

title

content

tags

created_at

updated_at

Indexes

IDX(portfolio_id)

Purpose

Manual observations.

Future AI learning.

---

# 31. Portfolio Tags

Table

portfolio_tag

Columns

id

name

description

color

---

Table

portfolio_tag_mapping

Columns

portfolio_id

tag_id

Indexes

Composite

(portfolio_id, tag_id)

---

# 32. Portfolio Audit

Purpose

Track important portfolio changes.

Table

portfolio_audit

Columns

id

portfolio_id

event

old_value

new_value

performed_by

source

performed_at

Purpose

Supports explainability.

---

# 33. Portfolio Relationships

```

Portfolio

│

├── Holding

│ ├── Transaction

│ └── Cash Flow

│

├── Snapshot

│

├── Goal

│

├── Metric

│

├── Note

│

└── Audit

```

---

# 34. Portfolio Index Strategy

Frequently Queried

Portfolio by Owner

Holdings by Portfolio

Transactions by Date

Transactions by Asset

Snapshots by Date

Metrics by Date

Goals by Status

Indexes

Composite

(portfolio_id, transaction_date)

(portfolio_id, asset_id)

(snapshot_date, portfolio_id)

(status, portfolio_id)

---

# 35. Constraints

Holding Quantity >= 0

Average Cost >= 0

NAV >= 0

Portfolio Value >= 0

Monthly SIP >= 0

Target Amount > 0

Snapshot Date unique per portfolio

---

# 36. Estimated Growth

Expected Records

Portfolio

<100

Holding

10–100

Transaction

10,000+

Snapshots

Daily

Goals

10–20

Cash Flow

10,000+

Metrics

Daily

Audit

Unlimited

Design assumes long-term history retention.

---

# 37. Future Extensions

Multiple portfolios

Joint portfolios

Family portfolios

Broker synchronization

Foreign currency holdings

Islamic inheritance planning

Tax calculations

Zakat calculations

Automatic reconciliation

---

# End of Part 2

# AI Investment Manager
# Database Design
# Part 3 – Asset Schema

---

# 38. Asset Module Overview

The Asset Module owns every investable instrument supported by the platform.

It is the system of record for:

Assets

Mutual Funds

Stocks

Categories

Sectors

Benchmarks

NAV History

Price History

Corporate Actions

Fund Holdings

Reference Data

No Portfolio-specific information is stored here.

---

# 39. Asset Table

Purpose

Represents every investable instrument.

Table

asset

Primary Key

id (UUID)

Columns

id

symbol

display_name

short_name

asset_type

currency

country

exchange

is_shariah

status

launch_date

provider

metadata_json

created_at

updated_at

deleted_at

Indexes

PK(id)

UNIQUE(symbol)

IDX(asset_type)

IDX(exchange)

IDX(status)

IDX(is_shariah)

Relationships

Asset

↓

Mutual Fund

↓

Stock

↓

ETF

↓

Future Asset Types

---

# 40. Mutual Fund Table

Purpose

Stores fund-specific information.

Table

mutual_fund

Primary Key

asset_id

Foreign Key

asset_id → asset.id

Columns

asset_id

management_company

fund_category_id

benchmark_id

expense_ratio

front_load

back_load

management_fee

minimum_investment

minimum_sip

aum

cash_percentage

equity_percentage

debt_percentage

dividend_policy

dividend_frequency

website

factsheet_url

prospectus_url

last_nav_update

Indexes

IDX(fund_category_id)

IDX(benchmark_id)

---

# 41. Stock Table

Purpose

Stores stock-specific information.

Table

stock

Primary Key

asset_id

Foreign Key

asset_id → asset.id

Columns

asset_id

isin

company_name

sector_id

industry

market_cap

free_float

shares_outstanding

eps

pe

pbv

roe

roa

debt_ratio

dividend_yield

last_financial_update

Indexes

IDX(sector_id)

IDX(industry)

IDX(market_cap)

---

# 42. Fund Category

Purpose

Reference table for fund classifications.

Table

fund_category

Columns

id

name

description

risk_level

display_order

created_at

Indexes

UNIQUE(name)

Examples

Money Market

Cash Management

Income

Equity

Balanced

Asset Allocation

Index

Commodity

International

---

# 43. Sector Table

Purpose

Reference table for business sectors.

Table

sector

Columns

id

name

industry

description

risk_level

cyclical

interest_rate_sensitive

inflation_sensitive

created_at

Indexes

UNIQUE(name)

Examples

Banking

Oil & Gas

Technology

Power

Fertilizer

Textile

Healthcare

Construction

---

# 44. Benchmark Table

Purpose

Represents benchmark indices.

Table

benchmark

Columns

id

name

benchmark_type

provider

description

currency

created_at

Indexes

UNIQUE(name)

Examples

KSE-100

KMI-30

Money Market Index

Islamic Equity Index

Custom Benchmark

---

# 45. NAV History

Purpose

Stores historical NAV values.

Table

nav_history

Columns

id

asset_id

nav_date

nav

adjusted_nav

daily_return

dividend

source

quality_score

created_at

Indexes

UNIQUE(asset_id, nav_date)

IDX(nav_date)

IDX(asset_id)

Rules

Immutable

No duplicate dates

---

# 46. Price History

Purpose

Stores historical market prices.

Table

price_history

Columns

id

asset_id

price_date

open_price

high_price

low_price

close_price

adjusted_close

volume

source

quality_score

created_at

Indexes

UNIQUE(asset_id, price_date)

IDX(price_date)

IDX(asset_id)

---

# 47. Corporate Action

Purpose

Stores events affecting assets.

Table

corporate_action

Columns

id

asset_id

action_type

announcement_date

effective_date

adjustment_factor

description

reference_url

created_at

Indexes

IDX(asset_id)

IDX(action_type)

IDX(effective_date)

Supported Types

Dividend

Bonus

Rights Issue

Split

Reverse Split

Merger

Acquisition

Fund Merger

Fund Closure

Delisting

---

# 48. Fund Holdings

Purpose

Provides look-through exposure.

Table

fund_holding

Columns

id

fund_asset_id

holding_asset_id

holding_name

holding_type

sector_id

weight_percentage

market_value

last_updated

Indexes

IDX(fund_asset_id)

IDX(sector_id)

Purpose

Enables indirect exposure analysis.

---

# 49. Asset Metrics

Purpose

Stores calculated metrics.

Table

asset_metric

Columns

id

asset_id

calculation_date

risk_score

expected_return

volatility

beta

alpha

sharpe_ratio

sortino_ratio

drawdown

momentum_score

quality_score

overall_score

Indexes

UNIQUE(asset_id, calculation_date)

IDX(asset_id)

IDX(calculation_date)

Purpose

Avoid repeated expensive calculations.

---

# 50. Asset Tags

Purpose

Flexible classification.

Table

asset_tag

Columns

id

name

description

color

---

Table

asset_tag_mapping

Columns

asset_id

tag_id

Indexes

UNIQUE(asset_id, tag_id)

Examples

High Growth

Defensive

Dividend

Value

Momentum

Islamic

Blue Chip

---

# 51. Asset Relationships

Asset

├── Mutual Fund

├── Stock

├── NAV History

├── Price History

├── Corporate Actions

├── Asset Metrics

├── Fund Holdings

├── Tags

├── Category

└── Benchmark

---

# 52. Asset Index Strategy

Frequently Queried

Asset by Symbol

Fund by Category

Stock by Sector

Latest NAV

Latest Price

Corporate Actions

Fund Holdings

Composite Indexes

(asset_type, is_shariah)

(sector_id, market_cap)

(asset_id, nav_date)

(asset_id, price_date)

---

# 53. Constraints

Asset Symbol unique

NAV > 0

Price > 0

Expense Ratio >= 0

Weight Percentage between 0–100

Only one benchmark per fund

Sector required for stocks

---

# 54. Estimated Growth

Assets

5,000+

Funds

500+

Stocks

2,500+

NAV Records

Millions

Price Records

Millions

Corporate Actions

Hundreds of thousands

Fund Holdings

Millions

The schema is optimized for long-term historical storage.

---

# 55. Future Extensions

ETF

REIT

Gold

Silver

Sukuk

International Stocks

International ETFs

Currencies

Commodities

Carbon Credits

Tokenized Assets

These asset classes should extend the existing Asset table through composition rather than requiring redesign.

---

# End of Part 3

# AI Investment Manager
# Database Design
# Part 4 – Market Intelligence Schema

---

# 56. Market Intelligence Module

Purpose

The Market Intelligence Module stores every external market observation used by the AI.

It owns:

- News
- Macroeconomic Indicators
- Sentiment
- Market Regimes
- Technical Indicators
- Economic Calendar
- Corporate Events
- Global Markets
- Market Signals

This module never stores portfolio data.

---

# 57. News Table

Purpose

Stores normalized financial news.

Table

market_news

Primary Key

id

Columns

id

headline

summary

content

publisher

author

publication_time

url

language

country

category

sentiment_score

credibility_score

impact_score

quality_score

status

created_at

Indexes

UNIQUE(url)

IDX(publication_time)

IDX(category)

IDX(country)

IDX(sentiment_score)

Rules

Original article never modified.

---

# 58. News Asset Mapping

Purpose

Maps articles to affected assets.

Table

market_news_asset

Columns

news_id

asset_id

relevance_score

Indexes

UNIQUE(news_id, asset_id)

Purpose

Many-to-many relationship.

---

# 59. News Sector Mapping

Table

market_news_sector

Columns

news_id

sector_id

relevance_score

Indexes

UNIQUE(news_id, sector_id)

---

# 60. Macroeconomic Indicator

Purpose

Stores economic releases.

Table

market_macro_indicator

Columns

id

indicator_name

country

release_date

frequency

forecast_value

actual_value

previous_value

unit

importance

trend

source

quality_score

created_at

Indexes

IDX(indicator_name)

IDX(release_date)

IDX(country)

Examples

SBP Policy Rate

Inflation

Core Inflation

GDP

Foreign Reserves

Exchange Rate

Oil Price

Gold Price

Current Account

Budget Deficit

Money Supply

---

# 61. Market Regime

Purpose

Represents overall market state.

Table

market_regime

Columns

id

regime

confidence

probability

start_date

end_date

is_active

supporting_model

created_at

Indexes

IDX(is_active)

IDX(start_date)

Rules

Only one active regime.

Historical records immutable.

---

# 62. Sentiment Table

Purpose

Stores aggregate sentiment.

Table

market_sentiment

Columns

id

calculation_date

overall_score

positive_percentage

neutral_percentage

negative_percentage

confidence

source_count

created_at

Indexes

UNIQUE(calculation_date)

---

# 63. Technical Indicator

Purpose

Stores calculated indicators.

Table

market_technical_indicator

Columns

id

asset_id

indicator_name

timeframe

calculation_date

value

signal

quality_score

created_at

Indexes

IDX(asset_id)

IDX(indicator_name)

IDX(calculation_date)

Supported Indicators

RSI

MACD

ATR

ADX

EMA

SMA

VWAP

Momentum

OBV

Bollinger Bands

---

# 64. Economic Calendar

Purpose

Stores scheduled events.

Table

economic_calendar

Columns

id

event_name

country

scheduled_datetime

expected_value

previous_value

actual_value

importance

status

created_at

Indexes

IDX(scheduled_datetime)

IDX(country)

IDX(importance)

Examples

SBP MPC

Federal Budget

Inflation Release

GDP Release

IMF Review

---

# 65. Global Market

Purpose

Tracks important international markets.

Table

global_market

Columns

id

market_name

symbol

country

asset_class

current_value

daily_change

weekly_change

monthly_change

volatility

correlation_score

last_updated

Indexes

UNIQUE(symbol)

IDX(country)

IDX(asset_class)

Examples

KSE-100

KMI-30

S&P 500

Nasdaq

Dow Jones

Brent

WTI

Gold

Silver

USD Index

Bitcoin

---

# 66. Market Signal

Purpose

Stores synthesized signals.

Table

market_signal

Columns

id

signal_name

signal_type

strength

confidence

generated_at

expiration_date

source_model

created_at

Indexes

IDX(signal_type)

IDX(generated_at)

Examples

Bullish Momentum

Risk-Off

Rate Cut Expected

Inflation Cooling

Sector Rotation

Liquidity Expansion

---

# 67. Intelligence Score

Purpose

Stores overall market intelligence.

Table

market_intelligence_score

Columns

id

calculation_date

overall_score

macro_score

technical_score

sentiment_score

news_score

global_score

regime_score

created_at

Indexes

UNIQUE(calculation_date)

Purpose

Single score representing market health.

---

# 68. Data Source Registry

Purpose

Tracks data providers.

Table

market_data_source

Columns

id

provider_name

provider_type

base_url

priority

refresh_interval

is_active

quality_score

last_successful_sync

created_at

Examples

MUFAP

PSX

SBP

Sarmaaya

Yahoo Finance

IMF

Trading Economics

RSS Feed

---

# 69. Data Import Log

Purpose

Audit all imports.

Table

market_import_log

Columns

id

provider_id

dataset

started_at

completed_at

records_processed

records_inserted

records_updated

status

error_message

duration_ms

Indexes

IDX(provider_id)

IDX(started_at)

IDX(status)

Purpose

Supports troubleshooting and monitoring.

---

# 70. Relationships

Market Intelligence

├── News

│ ├── Assets

│ └── Sectors

├── Macro Indicators

├── Market Regimes

├── Sentiment

├── Technical Indicators

├── Economic Calendar

├── Global Markets

├── Market Signals

├── Intelligence Scores

└── Data Sources

---

# 71. Index Strategy

Frequently Queried

Latest News

Latest Macro Releases

Active Market Regime

Current Sentiment

Latest Technical Indicators

Upcoming Economic Events

Latest Global Markets

Indexes

(publication_time DESC)

(calculation_date DESC)

(asset_id, indicator_name)

(is_active)

(provider_id, started_at)

---

# 72. Constraints

Only one active market regime.

News URL unique.

Technical indicator values numeric.

Sentiment score between -100 and +100.

Confidence between 0 and 100.

Importance between 1 and 5.

Historical observations immutable.

---

# 73. Estimated Growth

News

Millions

Technical Indicators

Hundreds of millions

Macro Releases

Hundreds of thousands

Signals

Millions

Import Logs

Millions

Schema optimized for append-heavy workloads.

---

# 74. Future Extensions

Alternative Data

Satellite Imagery

Weather Data

Shipping Indices

Social Sentiment

ESG Scores

Supply Chain Indicators

Cross-Market Correlations

Regime Forecasts

These additions should reuse the existing observation model without altering current tables.

---

# End of Part 4

# AI Investment Manager
# Database Design
# Part 5 – AI, Learning & Decision Engine Schema

---

# 75. AI Module Overview

Purpose

The AI Module stores every prediction, recommendation, model,
strategy, experiment and learning outcome.

It never stores raw market data.

It consumes:

Portfolio

↓

Assets

↓

Market Intelligence

↓

Feature Store

↓

Models

↓

Predictions

↓

Recommendations

↓

Learning

---

# 76. AI Model Registry

Purpose

Stores every ML and AI model.

Table

ai_model

Columns

id

name

display_name

model_type

framework

version

training_dataset

feature_set_version

training_date

accuracy

precision

recall

f1_score

auc

mape

rmse

status

artifact_path

checksum

created_at

Indexes

UNIQUE(name, version)

IDX(model_type)

IDX(status)

Examples

Fund Ranking Model

Return Prediction Model

Risk Prediction Model

LLM Recommendation Model

Portfolio Optimizer

---

# 77. Feature Store

Purpose

Stores engineered ML features.

Table

feature_store

Columns

id

entity_type

entity_id

feature_name

feature_value

feature_type

feature_version

calculation_date

quality_score

created_at

Indexes

(entity_type, entity_id)

(feature_name)

(calculation_date)

Purpose

Features are calculated once.

Used everywhere.

---

# 78. Prediction

Purpose

Stores AI predictions.

Table

prediction

Columns

id

portfolio_id

asset_id

model_id

prediction_type

prediction_horizon

prediction_date

predicted_return

predicted_price

predicted_nav

predicted_risk

predicted_volatility

confidence

explanation

status

created_at

Indexes

(asset_id)

(portfolio_id)

(model_id)

(prediction_date)

Rules

Predictions are immutable.

---

# 79. Prediction Evaluation

Purpose

Measures prediction quality.

Table

prediction_evaluation

Columns

id

prediction_id

actual_value

prediction_error

absolute_error

percentage_error

is_correct

evaluated_at

Indexes

(prediction_id)

(evaluated_at)

Purpose

Feeds Learning Engine.

---

# 80. Recommendation

Purpose

Stores generated recommendations.

Table

recommendation

Columns

id

portfolio_id

prediction_id

recommendation_type

priority

asset_id

from_asset_id

to_asset_id

recommended_amount

expected_return

expected_risk

confidence

reason

explanation

status

generated_at

expires_at

Indexes

(portfolio_id)

(status)

(priority)

Examples

BUY

SELL

SWITCH

WAIT

CONTINUE SIP

INCREASE SIP

PAUSE SIP

REDUCE EXPOSURE

---

# 81. Recommendation Execution

Purpose

Tracks recommendation execution.

Table

recommendation_execution

Columns

id

recommendation_id

execution_status

executed_amount

execution_date

execution_source

execution_notes

Indexes

(recommendation_id)

Purpose

Learning compares:

Recommended

vs

Executed

---

# 82. Strategy

Purpose

Represents investment strategy.

Table

strategy

Columns

id

name

version

description

risk_profile

minimum_confidence

rebalance_frequency

investment_style

is_active

created_at

Indexes

(name)

(is_active)

Examples

Aggressive Growth

Income

Balanced

Capital Preservation

Maximum Growth

---

# 83. Strategy Evaluation

Purpose

Measures strategy effectiveness.

Table

strategy_evaluation

Columns

id

strategy_id

evaluation_date

annual_return

max_drawdown

sharpe_ratio

sortino_ratio

volatility

win_rate

score

Indexes

(strategy_id)

(evaluation_date)

---

# 84. Learning Record

Purpose

Stores learning events.

Table

learning_record

Columns

id

recommendation_id

prediction_id

strategy_id

outcome

expected_return

actual_return

learning_score

confidence_adjustment

reward

penalty

feedback

evaluated_at

Indexes

(strategy_id)

(recommendation_id)

Purpose

Core of the Learning Engine.

---

# 85. Reinforcement Feedback

Purpose

Stores reward signals.

Table

reinforcement_feedback

Columns

id

learning_record_id

reward_signal

reward_reason

weight

created_at

Indexes

(learning_record_id)

Examples

Prediction Correct

Prediction Wrong

Market Shock

User Accepted

User Rejected

Strategy Success

---

# 86. Experiment

Purpose

Stores AI experiments.

Table

experiment

Columns

id

experiment_name

description

feature_set_version

model_version

strategy_version

dataset_version

start_date

end_date

status

results_json

created_at

Indexes

(experiment_name)

(status)

Purpose

Supports reproducible research.

---

# 87. Backtest

Purpose

Stores backtest runs.

Table

backtest

Columns

id

strategy_id

model_id

portfolio_id

start_date

end_date

initial_capital

final_value

annual_return

xirr

max_drawdown

volatility

benchmark_return

outperformed

score

created_at

Indexes

(strategy_id)

(model_id)

(portfolio_id)

---

# 88. Explainability

Purpose

Stores AI explanations.

Table

recommendation_explanation

Columns

id

recommendation_id

explanation_type

title

description

importance

supporting_data

created_at

Indexes

(recommendation_id)

Purpose

Human-readable AI.

---

# 89. Decision History

Purpose

Stores every AI decision.

Table

decision_history

Columns

id

portfolio_id

strategy_id

prediction_id

recommendation_id

decision_date

decision_score

confidence

decision_reason

market_regime

created_at

Indexes

(portfolio_id)

(decision_date)

Purpose

Full audit trail.

---

# 90. Model Performance

Purpose

Tracks model quality over time.

Table

model_performance

Columns

id

model_id

evaluation_date

accuracy

precision

recall

f1_score

rmse

mae

mape

auc

drift_score

created_at

Indexes

(model_id)

(evaluation_date)

---

# 91. AI Relationships

AI Model

├── Feature Store

├── Prediction

│

├── Prediction Evaluation

│

├── Recommendation

│ ├── Execution

│ └── Explanation

│

├── Learning Record

│ └── Reinforcement Feedback

│

├── Strategy

│ ├── Strategy Evaluation

│ └── Backtest

│

├── Experiment

│

└── Model Performance

---

# 92. Index Strategy

Frequently Queried

Latest Predictions

Open Recommendations

Learning History

Backtests

Experiments

Model Performance

Composite Indexes

(model_id, prediction_date)

(strategy_id, evaluation_date)

(portfolio_id, generated_at)

(recommendation_id, execution_status)

---

# 93. Constraints

Confidence 0–100

Expected Return numeric

Prediction immutable

Learning Record append-only

Recommendation linked to Prediction

Only active strategy executable

---

# 94. Estimated Growth

Predictions

Millions

Recommendations

Millions

Learning Records

Millions

Features

Hundreds of millions

Experiments

Thousands

Backtests

Hundreds of thousands

Schema optimized for analytical workloads.

---

# 95. Future Extensions

LLM Agents

Multi-Agent Collaboration

Portfolio Digital Twin

Bayesian Models

Transformer Models

RLHF

Federated Learning

Online Learning

AutoML

A/B Testing

Model Marketplace

These capabilities extend the schema without requiring redesign.

---

# End of Part 5

# AI Investment Manager
# Database Design
# Part 6 – Performance, Indexing, Partitioning & Data Lifecycle

---

# 96. Purpose

This section defines how the database remains performant as historical data grows.

Objectives

- Fast queries
- Predictable response times
- Efficient storage
- Low maintenance
- Horizontal scalability
- Long-term historical retention

---

# 97. Performance Principles

Prioritize:

Correctness

↓

Consistency

↓

Maintainability

↓

Performance

Avoid premature optimization.

Measure before optimizing.

---

# 98. Index Strategy

Indexes should support business queries.

Primary Keys

All tables

↓

UUID Primary Key

Foreign Keys

Indexed automatically.

Business Indexes

Examples

portfolio_id

asset_id

prediction_date

generated_at

status

Composite Indexes

Examples

(portfolio_id, asset_id)

(asset_id, nav_date)

(asset_id, price_date)

(model_id, prediction_date)

(strategy_id, evaluation_date)

(status, generated_at)

---

# 99. Covering Indexes

Frequently executed dashboard queries should use covering indexes.

Examples

Portfolio Dashboard

Latest Recommendations

Latest NAV

Latest Prices

Market Regime

Current Allocation

Recommendation Queue

---

# 100. Unique Constraints

Prevent duplicate business records.

Examples

Asset Symbol

NAV Date

Price Date

Recommendation Version

Strategy Version

Experiment Version

Provider + External ID

---

# 101. Materialized Views

Purpose

Avoid expensive calculations.

Examples

Current Portfolio Value

Latest NAV

Latest Prices

Top Performing Funds

Portfolio Allocation

Asset Performance

Recommendation Statistics

Market Summary

Model Leaderboard

Materialized views refreshed by scheduler.

---

# 102. Standard Views

Used for reporting.

Examples

Current Holdings

Latest Recommendations

Portfolio Overview

Fund Rankings

Stock Rankings

Market Dashboard

Learning Summary

Backtest Summary

Views never contain business logic.

---

# 103. Partitioning Strategy

Tables expected to grow significantly should be partitioned.

Partition by Date

nav_history

price_history

prediction

learning_record

market_news

import_log

Partition Interval

Monthly (default)

Future

Quarterly

Yearly

depending on volume.

---

# 104. Archival Strategy

Operational Database

↓

Recent Data

↓

Archive Database

↓

Cold Storage

Retention Examples

Import Logs

2 Years

Experiments

5 Years

News

Forever (compressed)

NAV

Forever

Transactions

Forever

Predictions

Forever

Learning Records

Forever

---

# 105. Compression

Large append-only datasets should be compressed.

Candidates

News

Import Logs

Historical Prices

Historical NAV

Prediction History

Learning Records

Compression performed during archival.

---

# 106. Data Lifecycle

Each table belongs to one lifecycle.

Hot Data

Frequently updated.

Examples

Portfolio

Holding

Recommendation

Warm Data

Frequently read.

Examples

Transactions

Current NAV

Current Prices

Cold Data

Historical only.

Examples

Old Predictions

Old Experiments

Archived News

Frozen Data

Immutable archive.

Never modified.

---

# 107. Caching Strategy

Frequently requested information should be cached.

Examples

Latest NAV

Current Prices

Market Regime

Latest Recommendations

Fund Rankings

Model Rankings

Portfolio Summary

Cache Invalidation

Time-based

Event-based

Manual

---

# 108. Read Optimization

Heavy analytical queries should avoid transactional tables.

Use

Materialized Views

Snapshots

Feature Store

Aggregated Tables

Read Replicas (future)

---

# 109. Write Optimization

Batch inserts preferred.

Bulk imports

↓

Validation

↓

Staging

↓

Production tables

Never perform expensive calculations during import.

---

# 110. Staging Tables

Purpose

Validate imported data before publishing.

Examples

staging_nav

staging_price

staging_news

staging_macro

staging_fund

staging_stock

Workflow

Import

↓

Validate

↓

Normalize

↓

Deduplicate

↓

Publish

---

# 111. Data Quality

Every imported dataset receives a quality score.

Metrics

Completeness

Freshness

Accuracy

Consistency

Reliability

Duplicate Rate

Quality Score stored with each dataset.

---

# 112. Query Guidelines

Avoid

SELECT *

Prefer

Explicit columns

Limit result sets.

Paginate large queries.

Use server-side filtering.

---

# 113. Snapshot Strategy

Snapshots reduce expensive recalculation.

Daily Portfolio Snapshot

Daily Market Snapshot

Daily Intelligence Snapshot

Daily Strategy Snapshot

Snapshots become historical records.

---

# 114. Time-Series Optimization

Historical datasets

NAV

Prices

Technical Indicators

Macro Releases

Signals

should be append-only.

Future migration to TimescaleDB should require no schema redesign.

---

# 115. Data Retention Policy

Portfolio

Forever

Transactions

Forever

NAV

Forever

Prices

Forever

Predictions

Forever

Recommendations

Forever

Learning

Forever

Logs

Configurable

Temporary Files

Automatically removed

---

# 116. Monitoring Metrics

Track

Query Duration

Index Usage

Slow Queries

Table Growth

Partition Size

Import Duration

Cache Hit Rate

Materialized View Refresh Time

Storage Utilization

---

# 117. Maintenance

Automated

Index Rebuild

Statistics Update

Vacuum (PostgreSQL)

Integrity Checks

Backup Verification

Partition Creation

Old Partition Archival

---

# 118. Disaster Recovery

Daily Backup

Point-in-Time Recovery

Weekly Verification

Quarterly Restore Test

Checksum Validation

Recovery documentation maintained.

---

# 119. Estimated Scale

Assets

10,000+

NAV Records

50 Million+

Price Records

100 Million+

Predictions

20 Million+

Learning Records

20 Million+

News

10 Million+

Events

Unlimited

Designed for 10+ years of growth.

---

# 120. Performance Targets

Portfolio Dashboard

< 300 ms

Recommendation Generation

< 5 seconds

Daily Market Refresh

< 15 minutes

NAV Import

< 5 minutes

Prediction Query

< 200 ms

Historical Backtest

< 60 seconds

---

# End of Part 6

# AI Investment Manager
# Database Design
# Part 7 – Database Operations, Versioning & Security

---

# 121. Purpose

This section defines how the database is operated throughout its lifecycle.

Objectives

- Safe schema evolution
- Reproducible deployments
- Secure data access
- Reliable backups
- Consistent environments
- Operational excellence

---

# 122. Migration Strategy

All schema changes must be migration-based.

Never manually modify production schemas.

Development Flow

Model Change

↓

Generate Migration

↓

Review

↓

Run Automated Tests

↓

Apply to Development

↓

Apply to Staging

↓

Apply to Production

Migration Tool

Alembic

Every migration must be:

- Versioned
- Reversible where practical
- Reviewed
- Tested

---

# 123. Schema Versioning

Maintain a database schema version.

Table

schema_version

Columns

id

version

description

migration_id

applied_at

applied_by

checksum

Purpose

Track exactly which schema version is deployed.

---

# 124. Seed Data

Reference data should be seeded automatically.

Examples

Currencies

Countries

Fund Categories

Sectors

Benchmark Types

Recommendation Types

Risk Levels

Investment Horizons

Market Regimes

Seed data must be:

Versioned

Repeatable

Idempotent

---

# 125. Environment Configuration

Supported environments

Development

Testing

Staging

Production

Each environment maintains:

Separate database

Separate credentials

Separate backups

Separate monitoring

Never share production credentials.

---

# 126. Backup Strategy

Backup Types

Full Backup

Incremental Backup

Transaction Log Backup (PostgreSQL)

Recommended Schedule

Full Backup

Daily

Incremental

Hourly

Transaction Logs

Every few minutes

Backups must be:

Encrypted

Verified

Restorable

---

# 127. Restore Strategy

Recovery objectives

Recovery Point Objective (RPO)

≤ 15 minutes

Recovery Time Objective (RTO)

≤ 60 minutes

Restore Tests

Monthly

Disaster Simulation

Quarterly

---

# 128. Security Model

Authentication

Application-managed

Authorization

Role-based

Least privilege

No shared administrative accounts.

---

# 129. Database Roles

Suggested Roles

db_admin

schema_admin

migration_service

application_read_write

application_read_only

analytics_read

reporting_read

backup_service

Each role has minimum required permissions.

---

# 130. Encryption

Encryption in Transit

TLS

Encryption at Rest

Database-native encryption

Encrypted Backups

Required

Sensitive configuration

Encrypted

---

# 131. Sensitive Data

Sensitive information includes

API Keys

Provider Tokens

Webhook Secrets

OAuth Tokens

User Credentials

Never store plaintext secrets.

Passwords must never be recoverable.

---

# 132. Audit Logging

Audit all:

Schema Changes

Permission Changes

Data Imports

Recommendation Executions

Model Deployments

Learning Runs

Backups

Restores

Audit logs are append-only.

---

# 133. Data Validation

Validation occurs in stages.

Import

↓

Schema Validation

↓

Business Validation

↓

Quality Checks

↓

Publishing

Rejected data is quarantined for review.

---

# 134. Monitoring

Monitor

Database Availability

Slow Queries

Connection Pool

Storage Growth

Index Usage

Failed Migrations

Replication Lag (future)

Backup Success

Restore Success

Import Failures

---

# 135. Observability

Every major operation should produce:

Structured Logs

Metrics

Tracing (future)

Examples

Import Duration

Recommendation Latency

Prediction Time

Backup Duration

Migration Duration

---

# 136. Health Checks

Database Health

Migration Status

Connection Status

Storage Capacity

Pending Backups

Pending Imports

Feature Store Freshness

Market Data Freshness

---

# 137. Maintenance Tasks

Automated Tasks

Vacuum (PostgreSQL)

Analyze Statistics

Refresh Materialized Views

Rebuild Indexes (as needed)

Archive Old Partitions

Verify Constraints

Clean Temporary Tables

Schedule maintenance during low-traffic windows.

---

# 138. Multi-Tenancy (Future)

Current

Single User

Future

Multi-User

Enterprise

Recommended approach

Tenant ID on business tables

Shared schema

Logical isolation

This minimizes future redesign.

---

# 139. Compliance Considerations

Financial records

Retained permanently unless regulations change.

Recommendations

Retained permanently.

Predictions

Retained permanently.

Learning Records

Retained permanently.

Deletion requests should preserve financial auditability where legally required.

---

# 140. Operational Checklist

Before every production release

✓ Backup verified

✓ Migrations tested

✓ Seed data validated

✓ Monitoring enabled

✓ Rollback plan prepared

✓ Performance benchmarks passed

✓ Security review completed

✓ Schema version updated

---

# End of Part 7

# AI Investment Manager
# Database Design
# Part 8 – Enterprise ER Model, Data Dictionary & Implementation Guide

---

# 141. Enterprise Entity Relationship Overview

The database is organized into bounded contexts aligned with the Domain Model.

Portfolio Module

├── portfolio
├── holding
├── transaction
├── portfolio_snapshot
├── portfolio_cashflow
├── portfolio_metric
├── investment_goal
├── portfolio_note
├── portfolio_tag
├── portfolio_tag_mapping
└── portfolio_audit

↓

references

↓

Asset Module

├── asset
├── mutual_fund
├── stock
├── benchmark
├── sector
├── fund_category
├── nav_history
├── price_history
├── corporate_action
├── fund_holding
├── asset_metric
├── asset_tag
└── asset_tag_mapping

↓

consumed by

↓

Market Intelligence

├── market_news
├── market_news_asset
├── market_news_sector
├── market_macro_indicator
├── market_sentiment
├── market_regime
├── market_signal
├── market_technical_indicator
├── global_market
├── market_intelligence_score
├── economic_calendar
├── market_data_source
└── market_import_log

↓

consumed by

↓

AI Module

├── ai_model
├── feature_store
├── prediction
├── prediction_evaluation
├── recommendation
├── recommendation_execution
├── recommendation_explanation
├── strategy
├── strategy_evaluation
├── learning_record
├── reinforcement_feedback
├── experiment
├── backtest
├── decision_history
└── model_performance

---

# 142. Dependency Rules

Allowed Dependencies

Portfolio

↓

Asset

↓

Market

↓

AI

↓

Learning

Dependencies are one-directional.

Lower modules never depend on higher modules.

No circular references.

---

# 143. Foreign Key Matrix

Portfolio

→ Holding

Portfolio

→ Transaction

Portfolio

→ Snapshot

Holding

→ Asset

Transaction

→ Asset

Mutual Fund

→ Asset

Stock

→ Asset

NAV History

→ Asset

Price History

→ Asset

Corporate Action

→ Asset

Technical Indicator

→ Asset

Prediction

→ Asset

Prediction

→ Portfolio

Recommendation

→ Prediction

Recommendation

→ Portfolio

Learning Record

→ Recommendation

Learning Record

→ Prediction

Backtest

→ Strategy

Backtest

→ Model

---

# 144. Common Columns

Every business table should include where applicable:

id

created_at

updated_at

deleted_at

version

status

metadata_json

These columns provide consistency across the schema.

---

# 145. UUID Standards

Primary Keys

UUID v7 (preferred)

Fallback

UUID v4

UUIDs are generated by the application layer.

Sequential integer identifiers are avoided.

---

# 146. Timestamp Standards

All timestamps stored in UTC.

Application converts to local time for presentation.

Preferred precision

Milliseconds

Columns

created_at

updated_at

deleted_at

executed_at

evaluated_at

published_at

snapshot_date

---

# 147. Monetary Values

Never use floating-point types.

Recommended

NUMERIC(20,8)

or equivalent ORM Decimal type.

Examples

Investment Amount

NAV

Price

Fees

Taxes

Returns

Cash Flow

---

# 148. JSON Usage Guidelines

JSON columns are allowed only for flexible metadata.

Examples

metadata_json

allocation_json

results_json

supporting_data

Never store core business relationships in JSON.

Those belong in relational tables.

---

# 149. Soft Delete Policy

Soft delete applies to:

Portfolio

Notes

Reports

Strategies

Configuration

Reference Data

Hard delete is allowed only for:

Temporary staging tables

Import caches

Failed transient jobs

Financial history is never deleted.

---

# 150. Immutable Tables

The following are append-only:

transaction

nav_history

price_history

prediction

prediction_evaluation

learning_record

market_news

market_macro_indicator

market_signal

market_import_log

Event Store (future)

These records are never updated after publication.

---

# 151. Data Dictionary (Core Tables)

| Table | Purpose | Owner |
|--------|---------|-------|
| portfolio | User investment portfolio | Portfolio Module |
| holding | Current asset positions | Portfolio Module |
| transaction | Immutable financial transactions | Portfolio Module |
| asset | Master investment instrument | Asset Module |
| mutual_fund | Fund-specific metadata | Asset Module |
| stock | Equity-specific metadata | Asset Module |
| nav_history | Historical NAV values | Asset Module |
| price_history | Historical market prices | Asset Module |
| market_news | Financial news | Market Intelligence |
| market_macro_indicator | Economic indicators | Market Intelligence |
| market_regime | Current and historical market regimes | Market Intelligence |
| prediction | AI forecasts | AI Module |
| recommendation | Generated investment advice | AI Module |
| learning_record | Learning outcomes | AI Module |
| backtest | Historical strategy testing | AI Module |

---

# 152. Naming Convention Summary

Tables

snake_case singular

Columns

snake_case

Indexes

idx_<table>_<column>

Unique Constraints

uq_<table>_<column>

Foreign Keys

fk_<table>_<referenced_table>

Check Constraints

ck_<table>_<rule>

Views

vw_<name>

Materialized Views

mv_<name>

---

# 153. ORM Mapping Guidelines

Each Aggregate Root maps to one primary ORM model.

Entities become related ORM models.

Value Objects should be represented as:

Embedded objects

Composite types

or immutable helper classes.

Repositories return Domain objects rather than ORM models.

---

# 154. Database Generation Order

Recommended implementation sequence

1. Reference Tables
2. Asset Module
3. Portfolio Module
4. Market Intelligence
5. AI Module
6. Learning Module
7. Reporting Module
8. Configuration Module
9. Views
10. Materialized Views
11. Seed Data
12. Performance Optimization

This order minimizes migration complexity.

---

# 155. Migration Roadmap

Phase 1

Core Schema

Phase 2

Reference Data

Phase 3

Historical Data

Phase 4

Market Intelligence

Phase 5

AI Models

Phase 6

Learning Engine

Phase 7

Backtesting

Phase 8

Notifications

Phase 9

Analytics

Phase 10

Production Optimization

---

# 156. Database Readiness Checklist

Before development begins:

✓ Naming standards approved

✓ Relationships validated

✓ Constraints reviewed

✓ Index strategy reviewed

✓ Partition strategy documented

✓ Seed data defined

✓ Migration process established

✓ Backup strategy approved

✓ Security model approved

✓ Monitoring plan defined

✓ Performance targets documented

---

# 157. Future Evolution

The schema is designed to support future capabilities without redesign.

Planned extensions include:

- Multi-user portfolios
- Family portfolio management
- Broker integrations
- Direct PSX trading
- International markets
- ETFs and REITs
- Sukuk and fixed-income instruments
- Tax optimization
- Zakat calculations
- AI agents
- Multi-model ensemble predictions
- Event sourcing
- CQRS
- Data warehouse integration
- Lakehouse architecture
- Real-time streaming

---

# 158. Conclusion

The database design provides:

- Strong alignment with Domain-Driven Design
- High normalization with selective optimization
- Historical accuracy
- Financial auditability
- AI and ML readiness
- Long-term scalability
- PostgreSQL-first implementation
- SQLite compatibility for development

This document is the authoritative specification for persistence and should be updated alongside any domain model changes.