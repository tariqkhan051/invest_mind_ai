"""Notification provider contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.domain.enums import NotificationChannel


@dataclass(frozen=True, slots=True)
class DeliveryResult:
    """Outcome of a notification delivery attempt."""

    success: bool
    message: str


class NotificationProvider(ABC):
    """Replaceable notification delivery channel."""

    channel: NotificationChannel

    @abstractmethod
    def send(self, title: str, body: str) -> DeliveryResult:
        """Deliver a notification."""

    @abstractmethod
    def is_enabled(self) -> bool:
        """Return True when the provider is configured and active."""
