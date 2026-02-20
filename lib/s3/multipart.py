#!/usr/bin/env python3
"""Модуль для multipart загрузки файлов в S3."""

import os
import logging
import boto3
import botocore
from botocore.exceptions import ClientError
from typing import List, Dict, Any, Optional
from .client import S3Client


class MultipartUploader:
    """Класс для multipart загрузки больших файлов в S3."""
    
    def __init__(self, s3_client: S3Client, logger: Optional[logging.Logger] = None):
        """
        Инициализирует multipart загрузчик.
        
        Args:
            s3_client: Клиент S3
            logger: Логгер (опционально)
        """
        self.s3_client = s3_client
        self.logger = logger or logging.getLogger(__name__)
    
    def upload_file(
        self,
        file_path: str,
        bucket: str,
        key: str,
        part_size_mb: int = 50
    ) -> Dict[str, Any]:
        """
        Загружает файл в S3 используя multipart upload.
        
        Args:
            file_path: Путь к файлу
            bucket: Имя бакета
            key: Ключ объекта в S3
            part_size_mb: Размер части в мегабайтах
        
        Returns:
            Результат загрузки
        
        Raises:
            ClientError: При ошибке загрузки
        """
        upload_id = None
        try:
            self.logger.info(f"Инициализация multipart upload для {key}")
            
            # Инициализация multipart upload
            mpu = self.s3_client.client.create_multipart_upload(Bucket=bucket, Key=key)
            upload_id = mpu["UploadId"]
            self.logger.info(f"Создан multipart upload: UploadId={upload_id}")
            
            parts = []
            part_size = part_size_mb * 1024 * 1024
            total_size = os.path.getsize(file_path)
            total_parts = (total_size + part_size - 1) // part_size
            self.logger.info(f"Размер файла {total_size:,} байт, частей будет {total_parts}")
            
            # Загрузка частей
            with open(file_path, "rb") as f:
                part_number = 1
                while True:
                    data = f.read(part_size)
                    if not data:
                        break
                    
                    self.logger.info(
                        f"Загрузка части {part_number}/{total_parts}, "
                        f"размер {len(data)} байт"
                    )
                    
                    response = self.s3_client.client.upload_part(
                        Bucket=bucket,
                        Key=key,
                        PartNumber=part_number,
                        UploadId=upload_id,
                        Body=data
                    )
                    
                    etag = response["ETag"]
                    self.logger.info(f"Часть {part_number} загружена, ETag={etag}")
                    parts.append({"PartNumber": part_number, "ETag": etag})
                    part_number += 1
            
            # Завершение multipart upload
            self.logger.info("Завершение multipart upload")
            result = self.s3_client.client.complete_multipart_upload(
                Bucket=bucket,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts}
            )
            self.logger.info(f"Загрузка завершена: {result}")
            return result
            
        except ClientError as e:
            self.logger.error(f"ClientError при multipart upload: {e}")
            if upload_id:
                self.logger.warning(f"Прерывание multipart upload {upload_id}")
                self._abort_upload(bucket, key, upload_id)
            raise
        except Exception as e:
            self.logger.exception(f"Неожиданная ошибка при multipart upload: {e}")
            if upload_id:
                self.logger.warning(f"Прерывание multipart upload {upload_id}")
                self._abort_upload(bucket, key, upload_id)
            raise
    
    def _abort_upload(self, bucket: str, key: str, upload_id: str) -> None:
        """Прерывает multipart upload."""
        try:
            self.s3_client.client.abort_multipart_upload(
                Bucket=bucket,
                Key=key,
                UploadId=upload_id
            )
        except Exception as e:
            self.logger.error(f"Ошибка при прерывании upload: {e}")
