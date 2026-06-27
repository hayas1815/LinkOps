"""
Custom exceptions for the Document module.
"""

from typing import Any


class DocumentException(Exception):
    """
    Base exception for all Document module errors.
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the base document exception.

        Args:
            message: Human-readable error details.
        """
        super().__init__(message)
        self.message = message


class DocumentNotFoundException(DocumentException):
    """
    Exception raised when a requested document is not found.
    """

    def __init__(
        self, document_id: Any = None, message: str | None = None
    ) -> None:
        """
        Initialize document not found exception.

        Args:
            document_id: Unique identifier of the missing document (UUID, string, etc.).
            message: Optional override for the error message.
        """
        self.document_id = document_id
        if not message:
            message = (
                f"Document with ID '{document_id}' was not found."
                if document_id
                else "Document not found."
            )
        super().__init__(message)


class DocumentAlreadyExistsException(DocumentException):
    """
    Exception raised when a document already exists in the system.
    """

    def __init__(
        self, identifier: Any = None, message: str | None = None
    ) -> None:
        """
        Initialize document already exists exception.

        Args:
            identifier: Value causing the conflict (e.g., duplicate filename or checksum).
            message: Optional override for the error message.
        """
        self.identifier = identifier
        if not message:
            message = (
                f"Document with identifier '{identifier}' already exists."
                if identifier
                else "Document already exists."
            )
        super().__init__(message)


class InvalidDocumentStateException(DocumentException):
    """
    Exception raised when an action is attempted on a document in an unsupported processing state.
    """

    def __init__(
        self, current_status: str | None = None, message: str | None = None
    ) -> None:
        """
        Initialize invalid document state exception.

        Args:
            current_status: The current status of the document.
            message: Optional override for the error message.
        """
        self.current_status = current_status
        if not message:
            message = (
                f"Document is in an invalid state for this operation (current status: '{current_status}')."
                if current_status
                else "Document is in an invalid state."
            )
        super().__init__(message)


class DocumentValidationException(DocumentException):
    """
    Exception raised when document validation checks fail.
    """

    def __init__(self, reason: str | None = None, message: str | None = None) -> None:
        """
        Initialize document validation exception.

        Args:
            reason: Explanation of why validation failed.
            message: Optional override for the error message.
        """
        self.reason = reason
        if not message:
            message = (
                f"Document validation failed: {reason}"
                if reason
                else "Document validation failed."
            )
        super().__init__(message)
