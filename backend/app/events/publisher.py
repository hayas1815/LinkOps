from abc import ABC, abstractmethod

from app.events.base import DomainEvent


class EventPublisher(ABC):
    """Abstract publisher interface for future messaging adapters."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        raise NotImplementedError
