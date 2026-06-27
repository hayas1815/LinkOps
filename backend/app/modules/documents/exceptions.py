"""
Custom exceptions for the Document module.
"""


class DocumentException(Exception):
    """
    Base exception for all Document module errors.
    """

    pass


class DocumentNotFoundException(DocumentException):
    """
    Exception raised when a requested document is not found.
    """

    pass
