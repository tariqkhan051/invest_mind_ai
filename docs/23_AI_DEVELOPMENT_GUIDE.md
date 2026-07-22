# AI Investment Manager
# AI Development Guide

Version: 1.0

Status: Mandatory Development Standard

---

# 1. Purpose

This document defines the mandatory development rules for all human developers and AI coding assistants (Cursor, GitHub Copilot, Claude, ChatGPT, etc.) contributing to the AI Investment Manager.

Its purpose is to ensure that every generated feature is:

- Consistent
- Maintainable
- Testable
- Explainable
- Secure
- Scalable

This document takes precedence over convenience.

---

# 2. Project Philosophy

This is **not** a CRUD application.

This is an intelligent investment decision platform.

Every module must contribute toward answering one question:

> **"Given everything we know today, what is the best investment decision?"**

Every implementation should maximize

- Maintainability
- Correctness
- Explainability
- Performance
- Testability

---

# 3. Development Principles

Always follow

- Clean Architecture
- Domain Driven Design
- SOLID
- DRY
- KISS
- YAGNI
- Explicit over Implicit

Avoid clever code.

Prefer readable code.

---

# 4. General Rules

Always

✓ Use type hints

✓ Write docstrings

✓ Write meaningful names

✓ Keep functions small

✓ Keep classes focused

✓ Handle errors gracefully

✓ Log important operations

✓ Write unit tests

Never

✗ Hardcode secrets

✗ Ignore exceptions

✗ Copy-paste code

✗ Use magic numbers

✗ Leave TODOs without issue references

✗ Break architecture

---

# 5. Clean Architecture Rules

Dependencies must always point inward.

Presentation

↓

Application

↓

Domain

↓

Infrastructure

Never reverse the dependency direction.

Domain must never depend on infrastructure.

Repositories abstract persistence.

Services contain business logic.

Controllers remain thin.

---

# 6. Layer Responsibilities

Presentation

- FastAPI
- Validation
- HTTP responses

Application

- Use Cases
- Services
- Commands
- Queries

Domain

- Entities
- Value Objects
- Business Rules

Infrastructure

- Database
- Collectors
- APIs
- External Services

---

# 7. Business Logic

Business rules belong only inside

Services

or

Domain Objects

Never inside

- Controllers
- API Routes
- Repositories
- Database Models

---

# 8. Repository Rules

Repositories

may

- Read
- Write
- Search

Repositories

must not

- Calculate
- Validate
- Apply business rules
- Call external APIs

---

# 9. Service Rules

Services

may

- Validate
- Calculate
- Coordinate
- Execute business logic

Services

must not

- Return HTTP responses
- Know SQL syntax
- Depend on FastAPI

---

# 10. AI Decision Engine Rules

Recommendations must always include

- Action
- Reason
- Confidence
- Risk
- Expected Benefit
- Supporting Evidence

Never generate recommendations without an explanation.

---

# 11. Learning Rules

The Learning Engine

must never

rewrite history.

Historical recommendations are immutable.

Learning creates new knowledge.

It never changes previous decisions.

---

# 12. Database Rules

Always use

SQLAlchemy ORM

Never execute raw SQL unless absolutely necessary.

Every migration must be reversible.

Historical records must remain immutable.

---

# 13. API Rules

Every endpoint shall

- Validate requests
- Return consistent responses
- Return appropriate HTTP status codes
- Document itself automatically

Prefer

GET

for reading

POST

for actions

PUT

for replacement

PATCH

for partial updates

DELETE

only where appropriate

---

# 14. Error Handling

Every exception should

- Be logged
- Return meaningful messages
- Avoid exposing internal details

Bad

```
Object reference failed.
```

Good

```
Portfolio transaction not found.
```

---

# 15. Logging

Always log

- Recommendation generation
- Data imports
- AI execution
- Errors
- Authentication
- Scheduler jobs

Never log

- Passwords
- Tokens
- Secrets
- Personal information

---

# 16. Security

Never commit

- Passwords
- API Keys
- Tokens
- Database credentials

Always use

Environment Variables

---

# 17. Configuration

Configuration belongs in

config/

Never hardcode

- URLs
- Thresholds
- API Keys
- Database settings
- Investment limits

---

# 18. Testing Requirements

Every feature must include

- Unit Tests
- Integration Tests (when applicable)

No feature is considered complete without tests.

---

# 19. Documentation Requirements

Whenever code changes

verify whether documentation also requires updates.

Update

Architecture

API

README

Roadmap

if necessary.

Documentation is part of the feature.

---

# 20. Naming Conventions

Classes

```
PortfolioService
```

Repositories

```
FundRepository
```

DTOs

```
FundDto
```

Entities

```
MutualFund
```

Enums

```
MarketRegime
```

Constants

```
MAX_RECOMMENDATIONS
```

Functions

```
calculate_xirr()
```

Variables

```
portfolio_value
```

Avoid abbreviations.

---

# 21. AI Code Generation Rules

Before generating code

AI must

1. Read relevant documentation

2. Understand architecture

3. Identify affected modules

4. Explain implementation plan

5. Generate code

6. Generate tests

7. Verify imports

8. Check formatting

9. Ensure type safety

10. Explain assumptions

---

# 22. Pull Request Checklist

Every feature must satisfy

✓ Tests Passing

✓ Ruff Passing

✓ Black Passing

✓ MyPy Passing

✓ Documentation Updated

✓ No Dead Code

✓ No Secrets

✓ No TODOs

✓ Proper Logging

✓ Error Handling

---

# 23. Performance Rules

Avoid

N+1 Queries

Repeated calculations

Duplicate API calls

Large memory allocations

Prefer

Caching

Pagination

Batch processing

Lazy loading

where appropriate.

---

# 24. AI Recommendation Rules

Never recommend

- Non-Shariah investments (when enabled)
- Investments without supporting evidence
- Switching funds without expected benefit
- Redeeming without explanation

Every recommendation must include

Why

Why Now

Why This

Risk

Confidence

Expected Return

---

# 25. Learning Engine Rules

Every recommendation shall record

Input Data

↓

Features

↓

Prediction

↓

Confidence

↓

User Action

↓

Market Outcome

↓

Prediction Accuracy

↓

Learning Update

Nothing should be discarded.

---

# 26. Code Quality Standards

Maximum Function Length

50 lines (guideline)

Maximum Class Length

300 lines (guideline)

Cyclomatic Complexity

Keep low.

Prefer composition over inheritance.

---

# 27. Dependencies

Before adding a dependency ask

Can the standard library solve this?

Is the dependency maintained?

Is it actively developed?

Is it secure?

Avoid unnecessary packages.

---

# 28. Git Standards

Branch Names

```
feature/portfolio-engine

feature/fund-ranking

bugfix/nav-import

refactor/learning-engine
```

Commit Messages

```
feat:

fix:

refactor:

docs:

test:

perf:

chore:
```

Example

```
feat: add AI fund ranking engine

fix: correct XIRR calculation

docs: update API documentation
```

---

# 29. Definition of Done

A feature is complete only if

✓ Requirements implemented

✓ Architecture respected

✓ Tests written

✓ Documentation updated

✓ Code reviewed

✓ Logging added

✓ Errors handled

✓ Performance acceptable

✓ No security violations

✓ AI explanation included (if applicable)

---

# 30. AI Assistant Prompting Rules

When asking an AI assistant to implement a feature:

Always provide

- Relevant documentation
- Expected behavior
- Acceptance criteria
- Constraints

Ask the AI to

1. Analyze before coding.
2. Identify edge cases.
3. Explain the implementation plan.
4. Implement incrementally.
5. Generate tests.
6. Review its own code for improvements.

Never ask the AI to blindly generate large amounts of code without context.

---

# 31. Guiding Principle

Every line of code should make the system

- More intelligent
- More maintainable
- More explainable
- More secure
- Easier to test

If a simpler solution exists that satisfies the requirements, choose the simpler solution.

---

# 32. Final Rule

The objective is **not** to generate the most code.

The objective is to build the **most reliable AI-powered investment advisor**.

Quality always takes precedence over speed.

---

# End of 23_AI_DEVELOPMENT_GUIDE.md