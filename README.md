# 🤖 AI Investment Manager

> An AI-powered, Shariah-compliant investment advisor focused on maximizing long-term wealth creation for Pakistani investors through intelligent portfolio analysis, market intelligence, and explainable recommendations.

---

# Vision

The goal of this project is to build an intelligent investment assistant that acts like a professional financial advisor.

Instead of simply tracking investments, the system continuously analyzes:

- Mutual Funds
- Pakistan Stock Exchange (PSX)
- Economic Indicators
- Market News
- Portfolio Performance
- Risk
- Historical Trends
- User Behaviour

to answer one question every day:

> **"What should I do with my investments today?"**

Possible recommendations include:

- ✅ Invest monthly amount
- ✅ Switch between mutual funds
- ✅ Hold current investments
- ✅ Redeem funds
- ✅ Buy selected PSX stocks
- ✅ Increase cash allocation
- ✅ Wait for better opportunities

Every recommendation is accompanied by:

- Confidence Score
- Risk Analysis
- Expected Return
- Supporting Evidence
- Human-readable Explanation

The AI never executes trades automatically.

The investor always remains in control.

---

# Key Features

## Portfolio Management

- Portfolio tracking
- Holdings management
- Transaction history
- Portfolio snapshots
- Cash management
- Asset allocation
- XIRR
- CAGR
- Performance analytics

---

## Mutual Fund Intelligence

- Daily NAV imports
- Historical NAV analysis
- Fund rankings
- Fund comparison
- AI Fund Scores
- Switching opportunities
- Risk metrics
- Category analysis

---

## Stock Intelligence

- PSX price history
- Technical indicators
- Fundamental analysis
- Sector analysis
- AI Stock Scores
- Opportunity detection
- Shariah compliance filtering

---

## Market Intelligence

- Interest Rates
- Inflation
- USD/PKR
- Oil & Gold Prices
- Economic Indicators
- News Analysis
- Market Sentiment
- Market Regime Detection

---

## AI Decision Engine

The AI combines:

Portfolio

+

Mutual Funds

+

Stocks

+

Market Intelligence

+

Learning Engine

↓

Daily Investment Recommendations

Examples

- Invest PKR 50,000 into MIF

- Switch PKR 250,000 from AMMF → MEF

- Hold Cash

- Buy MARI

- No Action Today

---

## Learning Engine

The system continuously learns from

Recommendations

↓

User Decisions

↓

Market Outcomes

↓

Prediction Accuracy

↓

Model Improvement

The objective is continuous improvement rather than static rule-based investing.

---

# Technology Stack

| Layer | Technology |
|---------|------------|
| Language | Python 3.13+ |
| Backend | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2 |
| Validation | Pydantic v2 |
| Scheduler | APScheduler |
| AI | Scikit-Learn |
| Dashboard | React + Vite |
| Charts | Recharts |
| Testing | Pytest |
| Linting | Ruff |
| Formatting | Black |
| Container | Docker |

---

# Project Structure

```
personal-investor/

docs/
src/
tests/
config/
data/
models/
reports/
logs/
scripts/
docker/
migrations/

README.md
requirements.txt
pyproject.toml
```

---

# Architecture

The project follows

- Domain Driven Design
- Clean Architecture
- Modular Monolith
- Repository Pattern
- Service Layer
- Dependency Injection
- Event-driven Internal Modules

Architecture

```
                 Dashboard

                      │

               REST API

                      │

                Services

                      │

     Portfolio / Funds / Stocks

                      │

          AI Decision Engine

                      │

   Learning + Optimization Engine

                      │

Repositories → Database

                      ▲

             Data Collectors

     MUFAP • PSX • SBP • News
```

---

# AI Decision Flow

```
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

Store Learning
```

---

# Current MVP Scope

The MVP includes

- Portfolio Management

- Mutual Fund Engine

- Stock Engine

- Market Intelligence

- AI Recommendation Engine

- Learning Engine

- Dashboard

- Reports

- REST APIs

- Scheduler

- Daily Recommendations

---

# Future Scope

Future versions may include

- WhatsApp Bot
- Telegram Bot
- Mobile App
- Broker Integration
- AMC Integration
- Automatic Statement Import
- Portfolio Optimization
- Goal Planning
- Retirement Planning
- Tax Optimization
- Multi-Agent AI
- Reinforcement Learning
- International Markets

---

# Development Workflow

```
Requirement

↓

Documentation

↓

Implementation

↓

Unit Tests

↓

Integration Tests

↓

Backtesting

↓

Code Review

↓

Deployment
```

---

# Coding Principles

- Clean Architecture
- SOLID
- DRY
- KISS
- Explicit Typing
- Explainable AI
- Immutable Historical Data
- No Hardcoded Secrets

---

# AI Development

This repository is designed to be developed alongside AI coding assistants.

All generated code must:

- Follow project architecture
- Include tests
- Include type hints
- Follow coding standards
- Preserve module boundaries
- Avoid unrelated changes

Refer to

```
docs/23_AI_DEVELOPMENT_GUIDE.md
```

and the complete specifications in

```
docs/
```

---

# Documentation

Project documentation

```
01_PROJECT_VISION.md

02_REQUIREMENTS.md

03_ARCHITECTURE.md

04_DOMAIN_MODEL.md

05_DATABASE_DESIGN.md

06_DATA_PIPELINES.md

07_AI_ARCHITECTURE.md

08_PROJECT_STRUCTURE.md

09_CODING_STANDARDS.md

10_TECH_STACK.md

11_DATA_COLLECTION.md

12_PORTFOLIO_ENGINE.md

13_MUTUAL_FUND_ENGINE.md

14_STOCK_ENGINE.md

15_MARKET_INTELLIGENCE_ENGINE.md

16_AI_DECISION_ENGINE.md

17_DASHBOARD.md

18_API.md

19_SECURITY.md

20_TESTING.md

21_ROADMAP.md

22_FUTURE_IDEAS.md

23_AI_DEVELOPMENT_GUIDE.md
```

---

# Project Status

Current Phase

✅ Documentation Complete

✅ Milestone 1–12 — MVP modules implemented

✅ Local bootstrap — seed assets, sample portfolio

✅ Live MUFAP / Al Meezan / PSX / SBP / news collectors

Next Phase

⏳ Milestone 13 — Production Deployment

---

# Getting Started (local analysis)

Run these steps once from the repo root:

```bash
# 1) Install into the project venv (required — system Python lacks deps like bs4)
uv sync

# 2) Bootstrap DB, seed assets, pull LIVE market data, generate advice
uv run python -m scripts.bootstrap
# optional: uv run python -m scripts.bootstrap --skip-news
# optional: uv run python -m scripts.bootstrap --reset-portfolio

# 3) Start API
uv run python -m src.main

# 4) Start dashboard (second terminal)
cd dashboard
npm install
npm run dev
```

Then open:

- API docs: http://localhost:8000/docs
- Dashboard: http://localhost:5173

Useful endpoints after bootstrap:

- `GET /api/v1/portfolio` — portfolio summary
- `GET /api/v1/funds` — fund analysis
- `GET /api/v1/stocks` — stock analysis
- `GET /api/v1/recommendations` — AI recommendations
- `POST /api/v1/assets/funds` / `POST /api/v1/assets/stocks` — register more assets
- `POST /api/v1/collectors/nav` — re-import live MUFAP + Al Meezan fund prices

Live sources (see `config/providers.yaml`):

- MUFAP daily NAV HTML
- Al Meezan fund prices (offer / repurchase / NAV, typically prior day)
- PSX Data Portal EOD timeseries (expanded watchlist)
- SBP homepage (policy rate, USD/PKR) + World Bank CPI
- Dawn / BBC Business RSS

Set `source: local` only if you need offline sample files.

Future

⏳ WhatsApp Integration

---

# Guiding Principles

This project exists to answer one question:

> **"Given everything we know today, what is the smartest investment decision for tomorrow?"**

The system should always be

- Explainable
- Data-driven
- Shariah-compliant
- Continuously learning
- Transparent
- Reliable
- User-controlled

The AI advises.

The investor decides.

---

# License

This project is intended for educational and personal investment management purposes.

Nothing produced by this system constitutes financial advice.

Users remain solely responsible for their investment decisions.

---

# Author

**Muhammad Tariq Khan**

MS Software Project Management

AI-Enhanced Software Project Management Researcher

FinTech | Artificial Intelligence | Investment Analytics

---