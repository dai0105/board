import boto3
import uuid
from django.conf import settings

def upload_to_r2_thread(file):
    
    ext = file.name.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    s3 = boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name="auto"
    )

    # ★ thread-media バケットにアップロード
    s3.upload_fileobj(
        file,
        settings.AWS_STORAGE_BUCKET_NAME,
        filename,
        ExtraArgs={"ContentType": file.content_type}
    )

    # 公開URLを返す
    return f"{settings.AWS_THREAD_PUBLIC_URL}/{filename}"