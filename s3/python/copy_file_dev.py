import boto3

# Создание клиента S3 с указанием конкретного endpoint
#session = boto3.Session(region_name='ru-1')
s3_client = boto3.client(
    's3',
    endpoint_url=''
)

# Пример использования: копирование объекта
source_bucket_name = '1be69fbc-file-storage'
source_key = 'twc-dbass-config.yaml'
destination_bucket_name = '50c17271-check-copy'
destination_key = 'twc-dbass-config.yaml'

copy_source = {
    'Bucket': source_bucket_name,
    'Key': source_key
}

response = s3_client.copy_object(
    Bucket=destination_bucket_name,
    Key=destination_key,
    CopySource=copy_source
)

print("Объект успешно скопирован.")
print(response)
