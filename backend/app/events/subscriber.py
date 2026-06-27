from abc import ABC, abstractmethod

from app.events.base import DomainEvent


class EventSubscriber(ABC):
    """Abstract subscriber interface for future event consumers."""

    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        raise NotImplementedError
