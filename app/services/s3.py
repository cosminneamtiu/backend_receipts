import os
import boto3
import uuid
from fastapi import UploadFile, HTTPException
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

# Load AWS config from .env
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

# Initialize the S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

async def upload_image_to_s3(file: UploadFile) -> str:
    """
    Uploads a file to AWS S3 and returns the public URL.
    """
    try:
        # 1. Generate a unique file name using UUID to prevent overwriting
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"receipts/{uuid.uuid4()}.{file_extension}"

        # 2. Read the file into memory
        file_contents = await file.read()

        # 3. Upload to S3
        s3_client.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=unique_filename,
            Body=file_contents,
            ContentType=file.content_type
        )
        # 4. Construct and return the public URL
        s3_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"
        return s3_url

    except ClientError as e:
        print(f"AWS S3 Upload Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image to cloud storage.")
    except Exception as e:
        print(f"General Upload Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the image.")