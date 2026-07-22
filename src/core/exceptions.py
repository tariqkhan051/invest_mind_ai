"""Domain and application exception hierarchy.

See docs/03_ARCHITECTURE.md §22 and docs/23_AI_DEVELOPMENT_GUIDE.md §14.
"""


class InvestMindError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ConfigurationError(InvestMindError):
    """Raised when application configuration is invalid."""


class DatabaseError(InvestMindError):
    """Raised when a database operation fails."""


class DataProviderUnavailable(InvestMindError):  # noqa: N818
    """Raised when an external data provider is unavailable."""


class PortfolioValidationError(InvestMindError):
    """Raised when portfolio data fails validation."""


class PortfolioNotFoundError(InvestMindError):
    """Raised when a requested portfolio does not exist."""


class FundNotFoundError(InvestMindError):
    """Raised when a requested mutual fund does not exist."""


class StockNotFoundError(InvestMindError):
    """Raised when a requested stock does not exist."""


class NewsNotFoundError(InvestMindError):
    """Raised when a requested news article does not exist."""


class RecommendationNotFoundError(InvestMindError):
    """Raised when a requested recommendation does not exist."""


class LearningRecordNotFoundError(InvestMindError):
    """Raised when a requested learning record does not exist."""


class ReportNotFoundError(InvestMindError):
    """Raised when a requested report does not exist."""


class NotificationNotFoundError(InvestMindError):
    """Raised when a requested notification does not exist."""


class PredictionFailed(InvestMindError):  # noqa: N818
    """Raised when a prediction model fails to execute."""


class RecommendationGenerationError(InvestMindError):
    """Raised when the AI decision engine cannot generate a recommendation."""


class AuthenticationError(InvestMindError):
    """Raised when authentication fails."""


class AuthorizationError(InvestMindError):
    """Raised when the user lacks permission for an operation."""
