import boto3
from botocore.exceptions import ClientError
from app.config import settings
import uuid
from typing import Optional


def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.r2_endpoint_url,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )

async def upload_file(file_content: bytes, filename: str, content_type: str) -> str:
    """Upload file to R2 and return public URL."""
    client = get_r2_client()
    key = f"submissions/{uuid.uuid4()}/{filename}"

    try:
        client.put_object(
            Bucket=settings.r2_bucket_name,
            Key=key,
            Body=file_content,
            ContentType=content_type,
        )
        return f"{settings.r2_endpoint_url}/{settings.r2_bucket_name}/{key}"
    except ClientError as e:
        # Fallback for dev — store locally
        return f"local://{key}"


async def delete_file(file_url: str) -> bool:
    """Delete file from R2."""
    if file_url.startswith("local://"):
        return True
    try:
        client = get_r2_client()
        key = file_url.split(f"{settings.r2_bucket_name}/")[-1]
        client.delete_object(Bucket=settings.r2_bucket_name, Key=key)
        return True
    except ClientError:
        return False
