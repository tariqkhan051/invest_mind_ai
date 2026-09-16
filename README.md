# 🤖 AI Investment Manager

> An AI-powered, Shariah-compliant investment advisor focused on maximizing long-term wealth creation for Pakistani investors through intelligent portfolio analysis, market intelligence, and explainable recommendations.

---

<details>
<summary><h2>Vision</h2></summary>

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

</details>

---

<details>
<summary><h2>Key Features</h2></summary>

<details>
<summary><h3>Portfolio Management</h3></summary>

- Portfolio tracking
- Holdings management
- Transaction history
- Portfolio snapshots
- Cash management
- Asset allocation
- XIRR
- CAGR
- Performance analytics

</details>

<details>
<summary><h3>Mutual Fund Intelligence</h3></summary>

- Daily NAV imports
- Historical NAV analysis
- Fund rankings
- Fund comparison
- AI Fund Scores
- Switching opportunities
- Risk metrics
- Category analysis

</details>

<details>
<summary><h3>Stock Intelligence</h3></summary>

- PSX price history
- Technical indicators
- Fundamental analysis
- Sector analysis
- AI Stock Scores
- Opportunity detection
- Shariah compliance filtering

</details>

<details>
<summary><h3>Market Intelligence</h3></summary>

- Interest Rates
- Inflation
- USD/PKR
- Oil & Gold Prices
- Economic Indicators
- News Analysis
- Market Sentiment
- Market Regime Detection

</details>

<details>
<summary><h3>AI Decision Engine</h3></summary>

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

</details>

<details>
<summary><h3>Learning Engine</h3></summary>

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

</details>

</details>

---

<details>
<summary><h2>Technology Stack</h2></summary>

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

</details>

---

<details>
<summary><h2>Project Structure</h2></summary>

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

</details>

---

<details>
<summary><h2>Architecture</h2></summary>

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

</details>

---

<details>
<summary><h2>AI Decision Flow</h2></summary>

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

</details>

---

<details>
<summary><h2>Current MVP Scope</h2></summary>

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

</details>

---

<details>
<summary><h2>Future Scope</h2></summary>

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

</details>

---

<details>
<summary><h2>Development Workflow</h2></summary>

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

</details>

---

<details>
<summary><h2>Coding Principles</h2></summary>

- Clean Architecture
- SOLID
- DRY
- KISS
- Explicit Typing
- Explainable AI
- Immutable Historical Data
- No Hardcoded Secrets

</details>

---

<details>
<summary><h2>AI Development</h2></summary>

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

</details>

---

<details>
<summary><h2>Documentation</h2></summary>

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

</details>

---

<details open>
<summary><h2>Project Status</h2></summary>

Current Phase

✅ Documentation Complete

✅ Milestone 1–12 — MVP modules implemented

✅ Local bootstrap — seed assets, sample portfolio

✅ Live MUFAP / Al Meezan / PSX / SBP / news collectors

Next Phase

⏳ Milestone 13 — Production Deployment

</details>

---

<details open>
<summary><h2>Getting Started (local analysis)</h2></summary>

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

</details>

---

<details>
<summary><h2>Guiding Principles</h2></summary>

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

</details>

---

<details>
<summary><h2>License</h2></summary>

This project is intended for educational and personal investment management purposes.

Nothing produced by this system constitutes financial advice.

Users remain solely responsible for their investment decisions.

</details>

---

<details>
<summary><h2>Author</h2></summary>

**Muhammad Tariq Khan**

MS Software Project Management

AI-Enhanced Software Project Management Researcher

FinTech | Artificial Intelligence | Investment Analytics

</details>
