#!/usr/bin/env python3
"""
Скрипт для multipart загрузки больших файлов в S3.
"""

import sys
import argparse
import os
import yaml
from pathlib import Path

# Добавляем корневую директорию в путь для импорта библиотек
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.s3.client import S3Client
from lib.s3.multipart import MultipartUploader
from lib.utils.logging import setup_logger


def load_s3_config(env: str = None) -> dict:
    """Загружает конфигурацию S3."""
    if env is None:
        env = os.getenv("ENV", "dev")
    
    config_path = Path(__file__).parent.parent.parent / "config" / "s3_config.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Конфигурация S3 не найдена: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    return {
        "endpoint_url": config.get("endpoint_url", "https://s3.twcstorage.ru"),
        "region": config.get("region", "ru-1"),
        "default_part_size_mb": config.get("multipart", {}).get("default_part_size_mb", 50)
    }


def parse_args():
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(description="Multipart загрузка файлов в S3")
    
    parser.add_argument(
        "--env",
        choices=["prod", "stage", "dev"],
        help="Окружение"
    )
    
    parser.add_argument(
        "--file",
        required=True,
        help="Путь к файлу для загрузки"
    )
    
    parser.add_argument(
        "--bucket",
        required=True,
        help="Имя бакета"
    )
    
    parser.add_argument(
        "--key",
        required=True,
        help="Ключ объекта в S3"
    )
    
    parser.add_argument(
        "--part-size-mb",
        type=int,
        help="Размер части в мегабайтах (по умолчанию из конфигурации)"
    )
    
    parser.add_argument(
        "--log-file",
        help="Путь к файлу логов"
    )
    
    return parser.parse_args()


def main():
    """Основная функция."""
    args = parse_args()
    
    # Проверяем существование файла
    if not os.path.exists(args.file):
        print(f"Ошибка: файл {args.file} не найден")
        sys.exit(1)
    
    # Загружаем конфигурацию
    s3_config = load_s3_config(args.env)
    
    # Настраиваем логирование
    logger = setup_logger(
        name="multipart_upload",
        log_file=args.log_file,
        level=os.getenv("LOG_LEVEL", "INFO")
    )
    
    # Создаем клиент S3
    try:
        s3_client = S3Client(
            endpoint_url=s3_config["endpoint_url"],
            region=s3_config["region"]
        )
        
        uploader = MultipartUploader(
            s3_client=s3_client,
            logger=logger
        )
        
        part_size_mb = args.part_size_mb or s3_config["default_part_size_mb"]
        
        logger.info(f"Начало multipart загрузки:")
        logger.info(f"  Файл: {args.file}")
        logger.info(f"  Бакет: {args.bucket}")
        logger.info(f"  Ключ: {args.key}")
        logger.info(f"  Размер части: {part_size_mb} MB")
        
        result = uploader.upload_file(
            file_path=args.file,
            bucket=args.bucket,
            key=args.key,
            part_size_mb=part_size_mb
        )
        
        logger.info("✅ Файл успешно загружен.")
        logger.info(f"Результат: {result}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
