#!/usr/bin/env python3
"""
Скрипт для удаления объектов из S3.
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
    """Загружает конфигурацию S3."""
    if env is None:
        import os
        env = os.getenv("ENV", "dev")
    
    config_path = Path(__file__).parent.parent.parent / "config" / "s3_config.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Конфигурация S3 не найдена: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    return {
        "endpoint_url": config.get("endpoint_url", "https://s3.twcstorage.ru"),
        "region": config.get("region", "ru-1")
    }


def parse_args():
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(description="Удаление объектов из S3")
    
    parser.add_argument(
        "--env",
        choices=["prod", "stage", "dev"],
        help="Окружение"
    )
    
    parser.add_argument(
        "--bucket",
        required=True,
        help="Имя бакета"
    )
    
    parser.add_argument(
        "--key",
        required=True,
        help="Ключ объекта для удаления"
    )
    
    return parser.parse_args()


def main():
    """Основная функция."""
    args = parse_args()
    
    # Загружаем конфигурацию
    s3_config = load_s3_config(args.env)
    
    # Создаем клиент S3
    try:
        s3_client = S3Client(
            endpoint_url=s3_config["endpoint_url"],
            region=s3_config["region"]
        )
        
        print(f"Удаление объекта: s3://{args.bucket}/{args.key}")
        
        response = s3_client.delete_object(
            bucket=args.bucket,
            key=args.key
        )
        
        print("\n✅ Объект успешно удален.")
        print(f"Ответ API: {response}")
        
    except Exception as e:
        print(f"\n❌ Ошибка при удалении: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
