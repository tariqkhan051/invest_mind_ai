"""Domain enumerations aligned with docs/04_DOMAIN_MODEL.md."""

from enum import StrEnum


class PortfolioStatus(StrEnum):
    """Lifecycle status of a portfolio."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"
    SIMULATION = "simulation"
    CLOSED = "closed"


class RiskProfile(StrEnum):
    """Investor risk tolerance."""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    VERY_AGGRESSIVE = "very_aggressive"


class InvestmentPreference(StrEnum):
    """Investment style preference."""

    SHARIAH_COMPLIANT = "shariah_compliant"
    CONVENTIONAL = "conventional"
    MIXED = "mixed"


class InvestmentObjective(StrEnum):
    """Primary investment objective."""

    WEALTH_CREATION = "wealth_creation"
    INCOME = "income"
    CAPITAL_PRESERVATION = "capital_preservation"
    BALANCED = "balanced"


class InvestmentHorizon(StrEnum):
    """Expected investment time horizon."""

    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class AssetType(StrEnum):
    """Supported investable asset types."""

    MUTUAL_FUND = "mutual_fund"
    MONEY_MARKET_FUND = "money_market_fund"
    INCOME_FUND = "income_fund"
    EQUITY_FUND = "equity_fund"
    BALANCED_FUND = "balanced_fund"
    CASH_MANAGEMENT_FUND = "cash_management_fund"
    STOCK = "stock"
    ETF = "etf"
    GOLD = "gold"
    SUKUK = "sukuk"
    REIT = "reit"


class AssetStatus(StrEnum):
    """Asset listing status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DELISTED = "delisted"
    SUSPENDED = "suspended"


class HoldingStatus(StrEnum):
    """Holding lifecycle status."""

    ACTIVE = "active"
    CLOSED = "closed"


class TransactionType(StrEnum):
    """Investment transaction types."""

    BUY = "buy"
    SELL = "sell"
    SWITCH_IN = "switch_in"
    SWITCH_OUT = "switch_out"
    DIVIDEND = "dividend"
    BONUS = "bonus"
    SPLIT = "split"
    ADJUSTMENT = "adjustment"
    FEE = "fee"
    CORRECTION = "correction"
    TRANSFER = "transfer"
    AUTOMATIC_SIP = "automatic_sip"
    MANUAL_INVESTMENT = "manual_investment"
    REDEMPTION = "redemption"


class TransactionStatus(StrEnum):
    """Transaction processing status."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class GoalStatus(StrEnum):
    """Investment goal status."""

    ACTIVE = "active"
    ACHIEVED = "achieved"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class CashflowType(StrEnum):
    """Portfolio cash flow direction."""

    INFLOW = "inflow"
    OUTFLOW = "outflow"


class MarketRegime(StrEnum):
    """Detected market environment."""

    STRONG_BULL = "strong_bull"
    BULL = "bull"
    NEUTRAL = "neutral"
    BEAR = "bear"
    STRONG_BEAR = "strong_bear"
    HIGH_INFLATION = "high_inflation"
    HIGH_INTEREST_RATE = "high_interest_rate"
    RECOVERY = "recovery"
    VOLATILE = "volatile"


class NewsCategory(StrEnum):
    """News classification categories."""

    ECONOMY = "economy"
    POLITICS = "politics"
    BANKING = "banking"
    ENERGY = "energy"
    TECHNOLOGY = "technology"
    CORPORATE_EARNINGS = "corporate_earnings"
    REGULATIONS = "regulations"
    GLOBAL_MARKETS = "global_markets"
    MUTUAL_FUNDS = "mutual_funds"
    GENERAL = "general"


class SentimentLabel(StrEnum):
    """News sentiment classification."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class InvestmentSignalType(StrEnum):
    """Market-level investment signals."""

    INCREASE_EQUITY = "increase_equity"
    INCREASE_MONEY_MARKET = "increase_money_market"
    INCREASE_INCOME_FUND = "increase_income_fund"
    HOLD_CASH = "hold_cash"
    REDUCE_RISK = "reduce_risk"
    FAVOR_DEFENSIVE = "favor_defensive"
    FAVOR_GROWTH = "favor_growth"


class AlertSeverity(StrEnum):
    """Market alert severity."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationType(StrEnum):
    """Investment recommendation actions."""

    NO_ACTION = "no_action"
    INVEST = "invest"
    BUY = "buy"
    SELL = "sell"
    SWITCH = "switch"
    REDEEM = "redeem"
    HOLD_CASH = "hold_cash"
    WAIT = "wait"
    CONTINUE_SIP = "continue_sip"


class RecommendationStatus(StrEnum):
    """Recommendation lifecycle status."""

    ACTIVE = "active"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IGNORED = "ignored"
    EXPIRED = "expired"


class FeedbackAction(StrEnum):
    """User feedback on a recommendation."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IGNORED = "ignored"
    MODIFIED = "modified"


class RiskLevel(StrEnum):
    """Recommendation risk level."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class LearningOutcome(StrEnum):
    """Result of evaluating a recommendation against reality."""

    PENDING = "pending"
    ACCURATE = "accurate"
    PARTIALLY_ACCURATE = "partially_accurate"
    INACCURATE = "inaccurate"
    NO_OUTCOME = "no_outcome"
    UNKNOWN = "unknown"


class SchedulerJobCategory(StrEnum):
    """Background job categories."""

    MARKET = "market"
    AI = "ai"
    LEARNING = "learning"
    SYSTEM = "system"


class SchedulerJobStatus(StrEnum):
    """Execution status for scheduler jobs."""

    SUCCESS = "success"
    FAILED = "failed"


class SchedulerJobTrigger(StrEnum):
    """How a scheduler job was started."""

    SCHEDULED = "scheduled"
    MANUAL = "manual"


class ReportType(StrEnum):
    """Investment report period types."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class ReportFormat(StrEnum):
    """Supported report output formats."""

    MARKDOWN = "markdown"
    HTML = "html"


class NotificationChannel(StrEnum):
    """Notification delivery channels."""

    CONSOLE = "console"
    EMAIL = "email"


class NotificationStatus(StrEnum):
    """Notification delivery status."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class NotificationType(StrEnum):
    """Notification event categories."""

    REPORT_READY = "report_ready"
    RECOMMENDATION = "recommendation"
    MARKET_ALERT = "market_alert"
    SYSTEM = "system"
