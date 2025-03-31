import boto3
from django.conf import settings
import uuid

def upload_to_s3(file_obj, bucket_name, folder="receipts"):
    s3 = boto3.client('s3', region_name=settings.AWS_REGION)  # ✅ no credentials

    file_extension = file_obj.name.split('.')[-1]
    filename = f"{folder}/{uuid.uuid4()}.{file_extension}"
    
    s3.upload_fileobj(file_obj, bucket_name, filename)
    
    file_url = f"https://{bucket_name}.s3.amazonaws.com/{filename}"
    return file_url
