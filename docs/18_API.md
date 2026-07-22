# AI Investment Manager
# API Specification

Version: 1.0

Status: MVP

---

# 1. Purpose

This document defines the REST API exposed by the AI Investment Manager.

Objectives

- Consistent API design
- Versioned endpoints
- Typed request/response models
- Predictable error handling
- Easy frontend integration
- AI-friendly implementation

Base URL

/api/v1

---

# 2. API Principles

The API shall

- Follow REST conventions
- Use JSON
- Be stateless
- Support pagination
- Return consistent error responses
- Use HTTPS in production

---

# 3. Authentication

MVP

Local Authentication

Future

- OAuth2
- Google Login
- Microsoft Login
- JWT Authentication

---

# 4. Standard Response

Success

```json
{
  "success": true,
  "message": "Operation completed",
  "data": {}
}
```

Error

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": []
}
```

---

# 5. Portfolio APIs

### Portfolio Summary

GET

```
/portfolio
```

Returns

- Portfolio Value
- Cash
- Total Return
- XIRR
- Allocation

---

### Holdings

GET

```
/portfolio/holdings
```

---

### Transactions

GET

```
/portfolio/transactions
```

---

POST

```
/portfolio/transactions
```

Create a new transaction.

---

DELETE

```
/portfolio/transactions/{id}
```

Future only.

Prefer reversal transactions.

---

### Snapshots

GET

```
/portfolio/snapshots
```

---

# 6. Mutual Fund APIs

### List Funds

GET

```
/funds
```

---

### Fund Details

GET

```
/funds/{id}
```

---

### NAV History

GET

```
/funds/{id}/history
```

---

### Rankings

GET

```
/funds/rankings
```

---

### Comparison

POST

```
/funds/compare
```

---

### Switch Opportunities

GET

```
/funds/switch-opportunities
```

---

# 7. Stock APIs

GET

```
/stocks
```

---

GET

```
/stocks/{symbol}
```

---

GET

```
/stocks/{symbol}/history
```

---

GET

```
/stocks/rankings
```

---

POST

```
/stocks/compare
```

---

GET

```
/stocks/opportunities
```

---

# 8. Market Intelligence APIs

GET

```
/market/summary
```

---

GET

```
/market/news
```

---

GET

```
/market/regime
```

---

GET

```
/market/economy
```

---

GET

```
/market/signals
```

---

GET

```
/market/alerts
```

---

# 9. AI Recommendation APIs

### Latest Recommendation

GET

```
/recommendations/latest
```

---

### Recommendation History

GET

```
/recommendations
```

---

### Recommendation Details

GET

```
/recommendations/{id}
```

---

### Generate Recommendation

POST

```
/recommendations/run
```

---

### Feedback

POST

```
/recommendations/{id}/feedback
```

Body

```json
{
  "action": "accepted"
}
```

Allowed actions

- accepted
- rejected
- ignored
- modified

---

# 10. Reports

GET

```
/reports
```

---

GET

```
/reports/daily
```

---

GET

```
/reports/monthly
```

---

POST

```
/reports/generate
```

---

# 11. Dashboard APIs

GET

```
/dashboard
```

Returns

- Portfolio Summary
- Market Summary
- Latest Recommendation
- Charts
- Recent Activity

---

# 12. Data Collection

Trigger collectors manually.

POST

```
/collectors/nav
```

---

POST

```
/collectors/stocks
```

---

POST

```
/collectors/news
```

---

POST

```
/collectors/macro
```

---

GET

```
/collectors/status
```

---

# 13. Scheduler APIs

GET

```
/scheduler/jobs
```

---

POST

```
/scheduler/jobs/run/{job}
```

---

GET

```
/scheduler/history
```

---

# 14. System APIs

Health

GET

```
/health
```

---

Readiness

GET

```
/ready
```

---

Version

GET

```
/version
```

---

# 15. Settings APIs

GET

```
/settings
```

---

PUT

```
/settings
```

Supported settings

- Monthly Investment
- Risk Profile
- Notification Preferences
- AI Confidence Threshold
- Shariah Mode

---

# 16. Pagination

List endpoints should support

```
?page=1

&page_size=25

&sort=name

&order=asc
```

---

# 17. Filtering

Examples

```
?category=equity

?amc=meezan

?risk=high

?from=2026-01-01

?to=2026-12-31
```

---

# 18. HTTP Status Codes

200

Success

201

Created

400

Bad Request

401

Unauthorized

403

Forbidden

404

Not Found

409

Conflict

422

Validation Error

500

Internal Server Error

---

# 19. API Versioning

Current

```
/api/v1
```

Future versions

```
/api/v2
```

Breaking changes require a new API version.

---

# 20. Success Criteria

The API layer is complete when

✓ Portfolio operations available

✓ Fund operations available

✓ Stock operations available

✓ Market intelligence available

✓ AI recommendations accessible

✓ Reports downloadable

✓ Scheduler manageable

✓ Health endpoints operational

✓ APIs documented automatically via FastAPI OpenAPI

---

# End of 18_API.md