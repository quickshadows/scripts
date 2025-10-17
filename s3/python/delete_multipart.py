import boto3

# Ваши учетные данные
aws_access_key_id = "AccessKey"
aws_secret_access_key = "SecretKey"
REGION = "ru-1"
BUCKET_NAME = "BUCKET_NAME"
ENDPOINT_URL = "https://s3.twcstorage.ru"


# Создаем сессию и клиента S3
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=REGION
)

s3_client = session.client('s3', endpoint_url=ENDPOINT_URL)

# Получаем список мультипарт-uploads
response = s3_client.list_multipart_uploads(Bucket=BUCKET_NAME)

# Проверяем, есть ли мультипарт-uploads
if 'Uploads' in response:
    for upload in response['Uploads']:
        upload_id = upload['UploadId']
        key = upload['Key']
        print(f'Удаление мультипарт-uploads: {key}, UploadId: {upload_id}')
        
        # Удаляем мультипарт-upload
        s3_client.abort_multipart_upload(Bucket=BUCKET_NAME, Key=key, UploadId=upload_id)
else:
    print('Нет мультипарт-uploads для удаления.')
