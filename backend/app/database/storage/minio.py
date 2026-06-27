from datetime import timedelta
from io import BytesIO

from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings
from app.database.interfaces import StorageService


class MinIOStorageService(StorageService):
    """MinIO implementation of storage service interface for local development."""

    def __init__(self) -> None:
        settings = get_settings()
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self.buckets = settings.minio_buckets

    def ensure_buckets(self) -> None:
        for bucket in self.buckets:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)

    def upload(self, *, bucket: str, object_name: str, data: bytes, content_type: str) -> None:
        payload = BytesIO(data)
        self.client.put_object(
            bucket,
            object_name,
            data=payload,
            length=len(data),
            content_type=content_type,
        )

    def download(self, *, bucket: str, object_name: str) -> bytes:
        response = self.client.get_object(bucket, object_name)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def delete(self, *, bucket: str, object_name: str) -> None:
        self.client.remove_object(bucket, object_name)

    def exists(self, *, bucket: str, object_name: str) -> bool:
        try:
            self.client.stat_object(bucket, object_name)
            return True
        except S3Error:
            return False

    def generate_url(self, *, bucket: str, object_name: str, expires_seconds: int = 3600) -> str:
        return self.client.presigned_get_object(
            bucket,
            object_name,
            expires=timedelta(seconds=expires_seconds),
        )

    def health_check(self) -> bool:
        try:
            for bucket in self.buckets:
                self.client.bucket_exists(bucket)
            return True
        except Exception:
            return False


minio_storage = MinIOStorageService()
