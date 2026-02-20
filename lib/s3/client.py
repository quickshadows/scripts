#!/usr/bin/env python3
"""Клиент для работы с S3."""

import os
import boto3
from typing import Optional


class S3Client:
    """Клиент для работы с S3 хранилищем."""
    
    def __init__(
        self,
        endpoint_url: str,
        region: str = "ru-1",
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None
    ):
        """
        Инициализирует S3 клиент.
        
        Args:
            endpoint_url: URL endpoint S3
            region: Регион
            access_key_id: AWS Access Key ID (если не указан, берется из переменных окружения)
            secret_access_key: AWS Secret Access Key (если не указан, берется из переменных окружения)
        """
        self.endpoint_url = endpoint_url
        self.region = region
        
        # Получаем credentials из параметров или переменных окружения
        access_key = access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        
        if not access_key or not secret_key:
            raise ValueError("Необходимо указать AWS_ACCESS_KEY_ID и AWS_SECRET_ACCESS_KEY")
        
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
    
    def copy_object(
        self,
        source_bucket: str,
        source_key: str,
        destination_bucket: str,
        destination_key: str
    ) -> dict:
        """
        Копирует объект из одного бакета в другой.
        
        Args:
            source_bucket: Исходный бакет
            source_key: Ключ исходного объекта
            destination_bucket: Целевой бакет
            destination_key: Ключ целевого объекта
        
        Returns:
            Ответ API с результатом копирования
        """
        copy_source = {
            "Bucket": source_bucket,
            "Key": source_key
        }
        
        return self.client.copy_object(
            Bucket=destination_bucket,
            Key=destination_key,
            CopySource=copy_source
        )
    
    def delete_object(self, bucket: str, key: str) -> dict:
        """
        Удаляет объект из бакета.
        
        Args:
            bucket: Имя бакета
            key: Ключ объекта
        
        Returns:
            Ответ API с результатом удаления
        """
        return self.client.delete_object(Bucket=bucket, Key=key)
    
    def list_objects(self, bucket: str, prefix: str = "") -> list:
        """
        Получает список объектов в бакете.
        
        Args:
            bucket: Имя бакета
            prefix: Префикс для фильтрации объектов
        
        Returns:
            Список объектов
        """
        response = self.client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        return response.get("Contents", [])
