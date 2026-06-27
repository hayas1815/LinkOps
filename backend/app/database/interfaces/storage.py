from abc import ABC, abstractmethod


class StorageService(ABC):
    """Abstract object storage service interface."""

    @abstractmethod
    def upload(self, *, bucket: str, object_name: str, data: bytes, content_type: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def download(self, *, bucket: str, object_name: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def delete(self, *, bucket: str, object_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, *, bucket: str, object_name: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def generate_url(self, *, bucket: str, object_name: str, expires_seconds: int = 3600) -> str:
        raise NotImplementedError
