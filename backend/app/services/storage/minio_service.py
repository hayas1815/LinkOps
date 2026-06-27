"""
Async MinIO storage service wrapper.

Defers blocking synchronous MinIO client calls to a thread pool using
``asyncio.to_thread`` to keep the FastAPI event loop unblocked.
"""

import asyncio
import logging
from app.database.storage.minio import minio_storage

logger = logging.getLogger(__name__)


class MinioService:
    """
    Async service wrapper for MinIO storage operations.

    Executes all standard MinIO API operations (upload, download, delete, exist check,
    URL generation) using ``asyncio.to_thread`` to prevent event loop blocking.
    """

    def __init__(self) -> None:
        self.client = minio_storage.client
        self.buckets = minio_storage.buckets

    async def ensure_bucket(self, bucket: str) -> None:
        """
        Check if a bucket exists, and create it if it does not.

        Args:
            bucket: Name of the bucket to verify or create.
        """
        exists = await asyncio.to_thread(self.client.bucket_exists, bucket)
        if not exists:
            await asyncio.to_thread(self.client.make_bucket, bucket)
            logger.info("Created MinIO bucket: %s", bucket)

    async def upload_file(
        self, bucket: str, object_name: str, data: bytes, content_type: str
    ) -> None:
        """
        Upload file payload data asynchronously.

        Args:
            bucket: Target bucket name.
            object_name: The destination object key path.
            data: Binary payload of the file.
            content_type: MIME type of the file.
        """
        # Ensure bucket exists prior to upload
        await self.ensure_bucket(bucket)

        await asyncio.to_thread(
            minio_storage.upload,
            bucket=bucket,
            object_name=object_name,
            data=data,
            content_type=content_type,
        )
        logger.info("Successfully uploaded %s to bucket %s", object_name, bucket)

    async def download_file(self, bucket: str, object_name: str) -> bytes:
        """
        Download file payload data asynchronously.

        Args:
            bucket: Source bucket name.
            object_name: Object key path.

        Returns:
            bytes: The downloaded file contents.
        """
        data = await asyncio.to_thread(
            minio_storage.download,
            bucket=bucket,
            object_name=object_name,
        )
        logger.info("Successfully downloaded %s from bucket %s", object_name, bucket)
        return data

    async def delete_file(self, bucket: str, object_name: str) -> None:
        """
        Remove an object from MinIO storage asynchronously.

        Args:
            bucket: Target bucket name.
            object_name: Object key path to delete.
        """
        await asyncio.to_thread(
            minio_storage.delete,
            bucket=bucket,
            object_name=object_name,
        )
        logger.info("Successfully deleted %s from bucket %s", object_name, bucket)

    async def file_exists(self, bucket: str, object_name: str) -> bool:
        """
        Check if an object exists in MinIO storage asynchronously.

        Args:
            bucket: Target bucket name.
            object_name: Object key path to verify.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        exists = await asyncio.to_thread(
            minio_storage.exists,
            bucket=bucket,
            object_name=object_name,
        )
        return exists

    async def generate_presigned_url(
        self, bucket: str, object_name: str, expires_seconds: int = 3600
    ) -> str:
        """
        Generate a presigned GET URL for temporary access asynchronously.

        Args:
            bucket: Target bucket name.
            object_name: Object key path.
            expires_seconds: URL expiration duration in seconds.

        Returns:
            str: Presigned URL string.
        """
        url = await asyncio.to_thread(
            minio_storage.generate_url,
            bucket=bucket,
            object_name=object_name,
            expires_seconds=expires_seconds,
        )
        return url
