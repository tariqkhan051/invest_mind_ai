# AI Investment Manager
# Coding Standards

Version: 1.0

Status: MVP

---

# 1. Purpose

This document defines the coding standards for the AI Investment Manager.

Objectives

- Maintain clean, consistent code
- Improve readability
- Reduce bugs
- Produce AI-friendly code
- Simplify maintenance

These standards apply to all source code.

---

# 2. General Principles

Follow these principles:

- Keep it simple (KISS)
- Don't Repeat Yourself (DRY)
- Single Responsibility Principle (SRP)
- Prefer composition over inheritance
- Write readable code before clever code
- Explicit is better than implicit
- Fail fast with meaningful errors

---

# 3. Python Version

Python Version

3.13+

All code should support the latest stable Python version.

---

# 4. Formatting

Use

- Ruff (linting)
- Black (formatting)

Do not manually format code.

Maximum line length

88 characters

Indentation

4 spaces

Never use tabs.

---

# 5. Naming Conventions

## Variables

Use descriptive snake_case names.

Good

```
portfolio_value
monthly_investment
risk_score
```

Bad

```
pv
x
temp
```

---

## Functions

snake_case

Good

```
calculate_xirr()
load_nav_history()
generate_recommendations()
```

---

## Classes

PascalCase

Examples

```
PortfolioService
FundCollector
RecommendationEngine
```

---

## Constants

UPPER_CASE

Example

```
MAX_PORTFOLIO_RISK
DEFAULT_TIMEOUT
```

---

## Files

snake_case.py

Example

```
portfolio_service.py
fund_repository.py
```

---

# 6. Type Hints

Every public function must include type hints.

Example

```python
def calculate_return(
    investment: Decimal,
    current_value: Decimal,
) -> Decimal:
    ...
```

Avoid using `Any` unless absolutely necessary.

---

# 7. Docstrings

Use Google-style docstrings for public classes and methods.

Example

```python
def calculate_xirr(...):
    """Calculate annualized XIRR for a portfolio.

    Args:
        transactions: Portfolio transactions.

    Returns:
        Annualized return.
    """
```

Private helper functions may omit docstrings if self-explanatory.

---

# 8. Imports

Import order

1. Standard library
2. Third-party packages
3. Local modules

Example

```python
from decimal import Decimal

from fastapi import APIRouter

from src.services.portfolio_service import PortfolioService
```

Avoid wildcard imports.

Never use

```python
from module import *
```

---

# 9. Logging

Never use

```python
print()
```

Always use logging.

Example

```python
logger.info(...)
logger.warning(...)
logger.error(...)
```

Sensitive information must never be logged.

---

# 10. Exceptions

Raise specific exceptions.

Good

```python
raise PortfolioNotFoundError()
```

Bad

```python
raise Exception()
```

Catch exceptions only when they can be handled meaningfully.

---

# 11. Configuration

Do not hardcode:

- API keys
- URLs
- Credentials
- File paths
- Risk thresholds
- Timeouts

Use configuration files or environment variables.

---

# 12. Database

Use SQLAlchemy ORM.

Rules

- No raw SQL unless justified.
- Use transactions.
- Keep repositories focused on persistence.
- Business logic belongs in services or engines.

---

# 13. API

FastAPI endpoints should:

- Validate input
- Return typed responses
- Never contain business logic
- Delegate work to services

---

# 14. Services

Services coordinate business workflows.

Services may call:

- Repositories
- Engines
- AI modules
- External collectors (through interfaces)

Services should not directly access database sessions.

---

# 15. Engines

Engines contain pure business logic.

Examples

- Portfolio calculations
- Risk scoring
- Ranking
- Optimization
- Technical indicators

Engines should avoid I/O wherever possible.

---

# 16. Collectors

Collectors are responsible only for external data retrieval.

They should:

- Download data
- Validate transport-level responses
- Return normalized objects

Collectors must not update the database directly.

---

# 17. AI Modules

AI components should be deterministic where possible.

Every prediction must include:

- Confidence score
- Model version
- Timestamp

AI code should be isolated from business logic.

---

# 18. Testing

Every new feature should include tests.

Minimum coverage

- Unit tests for business logic
- Integration tests for repositories and APIs

Bug fixes should include regression tests.

---

# 19. Git Conventions

Branch names

```
feature/portfolio
feature/nav-import

bugfix/xirr

hotfix/login

docs/database
```

Commit messages

```
feat:
fix:
docs:
refactor:
test:
chore:
```

Examples

```
feat: add NAV import scheduler
fix: correct XIRR calculation
docs: update API specification
```

---

# 20. Code Review Checklist

Before merging, verify:

✓ Code builds successfully

✓ Tests pass

✓ Type hints are complete

✓ No hardcoded secrets

✓ Logging added where appropriate

✓ No duplicate code

✓ Documentation updated if required

✓ Public APIs remain backward compatible

---

# 21. AI Coding Rules

When using AI coding assistants:

- Generate small, focused changes.
- Do not modify unrelated files.
- Preserve architecture.
- Follow this document.
- Prefer readability over clever optimizations.
- Generate tests with implementation.
- Explain major design decisions in pull requests.

---

# 22. Definition of Done

A feature is complete when:

✓ Code compiles

✓ Tests pass

✓ Linting passes

✓ Formatting passes

✓ Documentation updated (if needed)

✓ No TODOs remain for MVP functionality

✓ Feature works end-to-end

---

# End of 09_CODING_STANDARDS.md