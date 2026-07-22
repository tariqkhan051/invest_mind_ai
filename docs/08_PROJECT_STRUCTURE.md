# AI Investment Manager
# Project Structure

Version: 1.0

Status: MVP

---

# 1. Purpose

This document defines the project directory structure, module organization, dependency rules and coding boundaries.

The objective is to create a clean, scalable and AI-friendly codebase.

Goals

- Predictable structure
- Easy navigation
- Separation of concerns
- Domain-driven organization
- Easy testing
- Easy deployment
- AI coding friendly

---

# 2. Architecture Style

The project follows:

- Domain Driven Design (DDD)
- Clean Architecture
- Modular Monolith (MVP)
- Event-Driven Internal Communication
- Repository Pattern
- Dependency Injection
- Service-Oriented Business Logic

Future versions may evolve into microservices without major restructuring.

---

# 3. Root Directory

```

personal-investor/
│
├── docs/
├── src/
├── tests/
├── scripts/
├── migrations/
├── data/
├── models/
├── logs/
├── reports/
├── backups/
├── config/
├── docker/
├── .github/
├── requirements.txt
├── pyproject.toml
├── README.md
└── .env

```

---

# 4. Source Structure

```

src/

├── api/
├── core/
├── config/
├── database/
├── domain/
├── repositories/
├── services/
├── engines/
├── collectors/
├── ai/
├── scheduler/
├── tasks/
├── notifications/
├── dashboard/
├── reports/
├── utils/
└── main.py

```

---

# 5. Module Responsibilities

## api/

Contains:

- FastAPI routes
- Request validation
- Response models
- API versioning

Never place business logic here.

---

## core/

Contains:

- Dependency Injection
- Logging
- Exceptions
- Constants
- Middleware
- Security helpers

---

## config/

Contains

- Application settings
- Environment configuration
- Feature flags

---

## database/

Contains

- SQLAlchemy models
- Alembic integration
- Sessions
- Base classes

---

## domain/

Contains

Business entities only.

Examples

Portfolio

Holding

Transaction

Fund

Stock

Recommendation

Prediction

Goal

No database code.

No API code.

---

## repositories/

Responsible for database access.

Examples

PortfolioRepository

HoldingRepository

FundRepository

RecommendationRepository

Repositories never contain business rules.

---

## services/

Contains business use cases.

Examples

PortfolioService

InvestmentService

RecommendationService

MarketAnalysisService

Services coordinate repositories and engines.

---

## engines/

Contains calculation engines.

Examples

Portfolio Engine

Mutual Fund Engine

Stock Engine

Macro Engine

News Engine

Risk Engine

Optimization Engine

Engines contain pure business logic.

---

## collectors/

Contains external integrations.

Examples

MUFAP

PSX

News APIs

SBP

RSS

Collectors never modify business logic.

---

## ai/

Contains AI components.

Examples

Prediction

Learning

Scoring

Prompt templates

LLM integrations

Feature engineering

---

## scheduler/

Contains scheduled jobs.

Examples

Daily NAV update

News import

Portfolio snapshot

Recommendation generation

Learning cycle

---

## tasks/

Contains asynchronous background jobs.

Examples

Report generation

Data imports

Notifications

Backtesting

---

## notifications/

Contains

WhatsApp

Email

Dashboard alerts

Future push notifications

---

## reports/

Responsible for

PDF

Excel

CSV

Performance reports

Tax reports (future)

---

## dashboard/

Dashboard-specific backend services.

---

## utils/

General reusable utilities.

Examples

Date helpers

Math utilities

Formatting

Validators

---

# 6. Data Directory

```

data/

raw/

processed/

cache/

exports/

imports/

datasets/

backtests/

```

Purpose

Raw downloaded data is never overwritten.

---

# 7. Models Directory

Contains trained AI models.

```

models/

prediction/

classification/

optimization/

embeddings/

llm/

registry/

```

---

# 8. Configuration

```

config/

development.yaml

testing.yaml

production.yaml

logging.yaml

providers.yaml

features.yaml

risk.yaml

```

Configurations are version controlled.

---

# 9. Reports Directory

```

reports/

daily/

weekly/

monthly/

backtests/

portfolio/

```

Generated automatically.

---

# 10. Logging

```

logs/

application/

scheduler/

ai/

imports/

notifications/

errors/

```

Log rotation enabled.

---

# 11. Testing Structure

```

tests/

unit/

integration/

api/

collectors/

engines/

repositories/

ai/

performance/

fixtures/

```

Every module has corresponding tests.

---

# 12. Naming Conventions

Folders

snake_case

Python files

snake_case.py

Classes

PascalCase

Functions

snake_case()

Variables

snake_case

Constants

UPPER_CASE

Environment Variables

UPPER_CASE

Database Tables

snake_case

---

# 13. Dependency Rules

Allowed dependency flow

```

API

↓

Services

↓

Engines

↓

Repositories

↓

Database

```

AI modules may consume

Repositories

Engines

Feature Store

Collectors never call services.

Repositories never call APIs.

Database never depends on application code.

---

# 14. Feature Module Example

Example

Portfolio

```

portfolio/

api/

schemas/

service.py

repository.py

engine.py

models.py

validators.py

exceptions.py

tests/

```

Every new feature should follow this structure.

---

# 15. MVP Modules

The first implementation should include:

- Portfolio
- Transactions
- Holdings
- Mutual Funds
- Stocks
- Market Data
- News
- AI Recommendations
- Learning
- Dashboard
- Reports
- Notifications

Future modules can be added without restructuring.

---

# 16. Development Workflow

Feature Request

↓

Create Branch

↓

Implement

↓

Unit Test

↓

Integration Test

↓

Code Review

↓

Merge

↓

Deploy

---

# 17. Project Principles

- Keep modules small and cohesive.
- Prefer composition over inheritance.
- Avoid circular dependencies.
- Keep business logic framework-independent.
- Make every module independently testable.
- Favor configuration over hardcoded values.

---

# 18. Success Criteria

The project structure is considered successful when:

✓ Every file has a single responsibility.

✓ Business logic is independent of frameworks.

✓ Modules are easy to locate.

✓ AI coding tools can infer where new code belongs.

✓ Future features can be added without major refactoring.

---

# End of 08_PROJECT_STRUCTURE.md