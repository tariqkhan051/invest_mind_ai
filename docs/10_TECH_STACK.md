# AI Investment Manager
# Technology Stack

Version: 1.0

Status: MVP

---

# 1. Purpose

This document defines the official technology stack for the AI Investment Manager.

Objectives

- Standardize development
- Eliminate unnecessary technology debates
- Improve maintainability
- Ensure AI coding tools generate consistent code
- Support future scalability

All contributors should follow this stack unless explicitly approved otherwise.

---

# 2. Technology Overview

| Layer | Technology |
|--------|------------|
| Language | Python 3.13+ |
| Backend | FastAPI |
| ORM | SQLAlchemy 2.x |
| Database | PostgreSQL |
| Database Migration | Alembic |
| Validation | Pydantic v2 |
| Scheduler | APScheduler |
| AI / ML | Scikit-learn |
| Data Analysis | Pandas |
| Numerical Computing | NumPy |
| Dashboard | React + Vite |
| Charts | Recharts |
| HTTP Client | HTTPX |
| Testing | Pytest |
| Linting | Ruff |
| Formatting | Black |
| Type Checking | MyPy |
| Logging | Loguru |
| Containerization | Docker |
| CI/CD | GitHub Actions |

---

# 3. Backend

Framework

FastAPI

Reason

- Excellent performance
- Native async support
- Automatic OpenAPI documentation
- Strong typing
- Easy testing
- Excellent AI ecosystem compatibility

---

# 4. Programming Language

Python 3.13+

Reasons

- Mature AI ecosystem
- Excellent finance libraries
- Rapid development
- Strong community support

---

# 5. Database

Primary

PostgreSQL

Reasons

- Reliability
- ACID compliance
- JSON support
- Excellent indexing
- Full-text search
- Production ready

Development

SQLite may be used for quick local testing.

Production always uses PostgreSQL.

---

# 6. ORM

SQLAlchemy 2.x

Reasons

- Mature ecosystem
- Strong typing support
- Async capabilities
- Excellent Alembic integration

Repositories should access the ORM.

Business logic should not.

---

# 7. Database Migration

Alembic

Responsibilities

- Schema versioning
- Upgrade scripts
- Rollbacks
- Seed data support

Never modify production schemas manually.

---

# 8. API Validation

Pydantic v2

Responsibilities

- Request validation
- Response serialization
- Settings management
- DTOs

---

# 9. Background Scheduling

Current

APScheduler

Responsibilities

- Daily NAV updates
- News imports
- Portfolio snapshots
- Recommendation generation
- Report generation

Future

Celery

Only when distributed workers become necessary.

---

# 10. HTTP Client

HTTPX

Reasons

- Async support
- Better API than requests
- Timeout management
- Connection pooling

Collectors should use HTTPX.

---

# 11. AI Libraries

Current

Scikit-learn

Purpose

- Classification
- Regression
- Feature engineering
- Model evaluation

Future

- LightGBM
- XGBoost
- CatBoost
- PyTorch (if required)

Do not introduce complex deep learning until justified by measurable improvements.

---

# 12. Data Processing

Pandas

Purpose

- NAV processing
- Portfolio analysis
- Feature engineering
- Historical datasets

NumPy

Purpose

- Numerical calculations
- Statistical operations
- Matrix computations

---

# 13. Dashboard

Framework

React

Build Tool

Vite

Reasons

- Fast
- Large ecosystem
- Excellent chart libraries
- Easy API integration

---

# 14. Charts

Recharts

Primary charts

- Portfolio growth
- Asset allocation
- NAV history
- CAGR
- XIRR
- Performance comparison
- Risk analysis

---

# 15. Authentication

Current MVP

Local authentication

Future

- OAuth2
- Google Login
- Microsoft Login
- Multi-user support

---

# 16. Logging

Library

Loguru

Log Levels

DEBUG

INFO

WARNING

ERROR

CRITICAL

Sensitive information must never be logged.

---

# 17. Configuration

Use

Pydantic Settings

Environment Variables

Configuration Files

Do not hardcode

- URLs
- Secrets
- Passwords
- API Keys
- Thresholds

---

# 18. Testing

Framework

Pytest

Test Types

- Unit
- Integration
- API
- Regression

Future

Performance tests

Backtesting validation

---

# 19. Code Quality

Formatter

Black

Linter

Ruff

Type Checker

MyPy

Security Scanner

Bandit (future)

Dependency Scanner

pip-audit

---

# 20. Containerization

Docker

Use Docker Compose for

- PostgreSQL
- Backend
- Dashboard

Future

Kubernetes

Only if required.

---

# 21. CI/CD

GitHub Actions

Pipeline

Lint

↓

Format Check

↓

Type Check

↓

Tests

↓

Build

↓

Docker Image

↓

Deploy

---

# 22. File Storage

Current

Local storage

Used for

- Reports
- Logs
- AI models
- Datasets
- Backtests

Future

AWS S3 / Azure Blob Storage

---

# 23. Recommended Project Dependencies

Core

- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- HTTPX
- APScheduler

Data

- Pandas
- NumPy
- SciPy

AI

- Scikit-learn
- Joblib

Utilities

- Loguru
- Python-dotenv
- Rich
- Tenacity

Development

- Ruff
- Black
- MyPy
- Pytest

---

# 24. Technology Principles

Choose technologies that are

- Stable
- Well documented
- Actively maintained
- Widely adopted
- Easy to replace
- Production ready

Avoid introducing new libraries unless they provide clear value.

---

# 25. MVP Technology Scope

The first release will include

✓ FastAPI Backend

✓ PostgreSQL Database

✓ SQLAlchemy ORM

✓ APScheduler

✓ HTTPX Collectors

✓ Scikit-learn

✓ React Dashboard

✓ Docker Deployment

✓ GitHub Actions

Everything else can be added incrementally.

---

# End of 10_TECH_STACK.md