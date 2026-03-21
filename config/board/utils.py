import boto3
import uuid
from django.conf import settings

def upload_to_r2_thread(file):
    ext = file.name.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    s3 = boto3.client(
        "s3",
        endpoint_url=settings.R2_ENDPOINT,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name="auto"
    )

    # ★ thread-media バケットにアップロード
    s3.upload_fileobj(
        file,
        settings.R2_THREAD_BUCKET_NAME,
        filename,
        ExtraArgs={"ContentType": file.content_type}
    )

    # 公開URLを返す
    return f"{settings.R2_THREAD_PUBLIC_URL}/{filename}"