"""
Custom exceptions for the Conversations module.
"""

from typing import Any


class ConversationException(Exception):
    """
    Base exception for all Conversation module errors.
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the base conversation exception.

        Args:
            message: Human-readable error details.
        """
        super().__init__(message)
        self.message = message


class ConversationNotFoundException(ConversationException):
    """
    Exception raised when a requested conversation is not found.
    """

    def __init__(
        self, conversation_id: Any = None, message: str | None = None
    ) -> None:
        """
        Initialize conversation not found exception.

        Args:
            conversation_id: Unique identifier of the missing conversation (UUID, string, etc.).
            message: Optional override for the error message.
        """
        self.conversation_id = conversation_id
        if not message:
            message = (
                f"Conversation with ID '{conversation_id}' was not found."
                if conversation_id
                else "Conversation not found."
            )
        super().__init__(message)
