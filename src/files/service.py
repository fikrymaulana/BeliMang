import uuid
from io import BytesIO
from minio import Minio
from minio.error import S3Error
from ..config import settings

class MinIOService:
    def __init__(self):
        self.client = Minio(
            settings.minio_public_url,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False  # Set to True if using HTTPS
        )
        self.bucket_name = settings.minio_bucket

    def ensure_bucket_exists(self):
        """Ensure the bucket exists, create if it doesn't"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"Error creating bucket: {e}")
            raise

    async def upload_image(self, file_data: bytes, file_extension: str) -> str:
        """Upload image to MinIO and return the file URL"""
        try:
            # Generate UUID for filename
            file_uuid = str(uuid.uuid4())
            filename = f"{file_uuid}.{file_extension}"

            # Ensure bucket exists
            self.ensure_bucket_exists()

            # Upload file
            file_buffer = BytesIO(file_data)
            file_buffer.seek(0)

            self.client.put_object(
                self.bucket_name,
                filename,
                file_buffer,
                length=len(file_data),
                content_type=f"image/{file_extension}"
            )

            # Return the public URL
            return f"https://{settings.minio_public_url}/{self.bucket_name}/{filename}"

        except S3Error as e:
            print(f"Error uploading to MinIO: {e}")
            raise

# Global MinIO service instance
minio_service = MinIOService()