"""Unit tests for exception hierarchy."""

from src.core.exceptions import (
    FundNotFoundError,
    InvestMindError,
    PortfolioNotFoundError,
    RecommendationGenerationError,
)


def test_investmind_error_message() -> None:
    """Base exception should expose a message attribute."""
    error = InvestMindError("Something went wrong")
    assert error.message == "Something went wrong"
    assert str(error) == "Something went wrong"


def test_domain_exceptions_inherit_base() -> None:
    """Domain exceptions should inherit from InvestMindError."""
    assert issubclass(PortfolioNotFoundError, InvestMindError)
    assert issubclass(FundNotFoundError, InvestMindError)
    assert issubclass(RecommendationGenerationError, InvestMindError)
