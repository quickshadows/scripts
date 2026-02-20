#!/usr/bin/env python3
"""
Универсальный скрипт для копирования объектов в S3.
Заменяет copy_file_prod.py и copy_file_dev.py единым решением.
"""

import sys
import argparse
import yaml
from pathlib import Path

# Добавляем корневую директорию в путь для импорта библиотек
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.s3.client import S3Client
from lib.utils.config_loader import load_config


def load_s3_config(env: str = None) -> dict:
    """
    Загружает конфигурацию S3 для указанного окружения.
    
    Args:
        env: Окружение (prod, stage, dev). Если не указано, берется из переменной окружения ENV.
    
    Returns:
        Словарь с конфигурацией S3
    """
    if env is None:
        import os
        env = os.getenv("ENV", "dev")
    
    config_path = Path(__file__).parent.parent.parent / "config" / "s3_config.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Конфигурация S3 не найдена: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # Получаем бакеты для указанного окружения
    buckets = config.get("buckets", {}).get(env, {})
    
    return {
        "endpoint_url": config.get("endpoint_url", "https://s3.twcstorage.ru"),
        "region": config.get("region", "ru-1"),
        "source_bucket": buckets.get("source"),
        "destination_bucket": buckets.get("destination")
    }


def parse_args():
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Копирование объектов в S3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Копировать объект для production
  python copy.py --env prod --source-key config.yaml --dest-key config.yaml
  
  # Копировать объект для dev с указанием бакетов
  python copy.py --env dev --source-bucket bucket1 --dest-bucket bucket2 --source-key file.txt --dest-key file.txt
        """
    )
    
    parser.add_argument(
        "--env",
        choices=["prod", "stage", "dev"],
        help="Окружение (prod, stage, dev). Если не указано, берется из переменной ENV"
    )
    
    parser.add_argument(
        "--source-bucket",
        help="Исходный бакет (если не указан, берется из конфигурации)"
    )
    
    parser.add_argument(
        "--dest-bucket",
        help="Целевой бакет (если не указан, берется из конфигурации)"
    )
    
    parser.add_argument(
        "--source-key",
        required=True,
        help="Ключ исходного объекта"
    )
    
    parser.add_argument(
        "--dest-key",
        help="Ключ целевого объекта (по умолчанию равен source-key)"
    )
    
    return parser.parse_args()


def main():
    """Основная функция."""
    args = parse_args()
    
    # Загружаем конфигурацию
    s3_config = load_s3_config(args.env)
    
    # Определяем бакеты
    source_bucket = args.source_bucket or s3_config.get("source_bucket")
    dest_bucket = args.dest_bucket or s3_config.get("destination_bucket")
    dest_key = args.dest_key or args.source_key
    
    if not source_bucket:
        print("Ошибка: исходный бакет не указан и не найден в конфигурации")
        sys.exit(1)
    
    if not dest_bucket:
        print("Ошибка: целевой бакет не указан и не найден в конфигурации")
        sys.exit(1)
    
    # Создаем клиент S3
    try:
        s3_client = S3Client(
            endpoint_url=s3_config["endpoint_url"],
            region=s3_config["region"]
        )
        
        print(f"Копирование объекта:")
        print(f"  Из: s3://{source_bucket}/{args.source_key}")
        print(f"  В:  s3://{dest_bucket}/{dest_key}")
        
        response = s3_client.copy_object(
            source_bucket=source_bucket,
            source_key=args.source_key,
            destination_bucket=dest_bucket,
            destination_key=dest_key
        )
        
        print("\n✅ Объект успешно скопирован.")
        print(f"Ответ API: {response}")
        
    except Exception as e:
        print(f"\n❌ Ошибка при копировании: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
