#!/usr/bin/env python3
"""
Универсальный скрипт для создания баз данных.
Утилита для создания БД через Timeweb Cloud API.
"""

import sys
import argparse
import yaml
from pathlib import Path

# Добавляем lib в путь для импорта библиотек
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from db.api_client import TimewebAPIClient
from db.ip_manager import IPManager
from db.database_factory import DatabaseFactory
from utils.config_loader import load_config, validate_config


def load_database_config(env: str) -> dict:
    """
    Загружает конфигурацию баз данных для указанного окружения.

    Args:
        env: Окружение (prod, stage, dev)

    Returns:
        Словарь с конфигурацией БД
    """
    config_path = Path(__file__).parent / "config" / "environments" / f"{env}.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Конфигурация для окружения '{env}' не найдена: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config.get("databases", {})


def get_database_types_config() -> dict:
    """
    Загружает mapping типов БД из config/db_config.yaml (если есть).
    Нужно, чтобы preset_id был опциональным в env-конфиге.
    """
    cfg_path = Path(__file__).parent / "config" / "db_config.yaml"
    if not cfg_path.exists():
        return {}
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return (cfg.get("database_types") or {})


def parse_args():
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Создание баз данных через Timeweb Cloud API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Создать все PostgreSQL базы для production
  ./create_all.py --env prod --db-type postgres

  # Создать MySQL кластер для staging
  ./create_all.py --env stage --db-type mysql --cluster

  # Создать все базы для production
  ./create_all.py --env prod --db-type all
        """,
    )

    parser.add_argument(
        "--env",
        required=True,
        choices=["prod", "stage", "dev"],
        help="Окружение (prod, stage, dev)",
    )

    parser.add_argument(
        "--db-type",
        required=True,
        choices=["mysql", "postgres", "redis", "mongodb", "opensearch", "clickhouse", "kafka", "rabbitmq", "all"],
        help="Тип базы данных (mysql, postgres, redis, mongodb, opensearch, clickhouse, kafka, rabbitmq, all)",
    )

    parser.add_argument(
        "--cluster",
        action="store_true",
        help="Создавать кластер вместо одиночной БД",
    )

    parser.add_argument(
        "--admin-password",
        help="Пароль администратора (по умолчанию из конфигурации)",
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Интерактивный режим с меню",
    )

    return parser.parse_args()


def interactive_menu():
    """Показывает интерактивное меню для выбора опций."""
    print("\n" + "=" * 60)
    print("Создание баз данных через Timeweb Cloud API")
    print("=" * 60)
    print("\nВыберите вариант создания баз данных:\n")
    print("1 — Только PostgreSQL (single)")
    print("2 — Только MySQL (single)")
    print("3 — Redis (single)")
    print("4 — MongoDB (single)")
    print("5 — OpenSearch (single)")
    print("6 — ClickHouse (single)")
    print("7 — Kafka (single)")
    print("8 — RabbitMQ (single)")
    print("9 — Все базы (single)")
    print("10 — Только PostgreSQL (cluster)")
    print("11 — Только MySQL (cluster)")
    print("12 — Все базы (cluster)")
    print("0 — Выход")

    choice = input("\nВаш выбор: ").strip()

    if choice == "0":
        print("Выход.")
        sys.exit(0)

    env_choice = input("Окружение (prod/stage/dev) [prod]: ").strip() or "prod"

    db_type_map = {
        "1": "postgres",
        "2": "mysql",
        "3": "redis",
        "4": "mongodb",
        "5": "opensearch",
        "6": "clickhouse",
        "7": "kafka",
        "8": "rabbitmq",
        "9": "all",
        "10": "postgres",
        "11": "mysql",
        "12": "all",
    }

    is_cluster = choice in ["10", "11", "12"]
    db_type = db_type_map.get(choice)

    if not db_type:
        print("Неверный выбор.")
        sys.exit(1)

    return env_choice, db_type, is_cluster


def main():
    """Основная функция."""
    # Проверяем интерактивный режим
    if "--interactive" in sys.argv or len(sys.argv) == 1:
        env, db_type, is_cluster = interactive_menu()
        admin_password = None
    else:
        args = parse_args()
        env = args.env
        db_type = args.db_type
        is_cluster = args.cluster
        admin_password = args.admin_password

    # Загружаем конфигурацию
    print(f"\nЗагрузка конфигурации для окружения: {env}")
    config = load_config(env)
    validate_config(config)

    # Инициализируем клиенты
    api_client = TimewebAPIClient(
        token=config["timeweb_token"],
        network_id=config["network_id"],
        project_id=config["project_id"],
        availability_zone=config.get("availability_zone", "spb-3"),
        base_url_v1=config.get("api_base_url_v1"),
        base_url_v2=config.get("api_base_url_v2"),
        databases_url=config.get("databases_url"),
    )

    ip_manager = IPManager(
        api_client=api_client,
        subnet_base=config.get("subnet_base", "192.168.0"),
    )

    factory = DatabaseFactory(api_client=api_client, ip_manager=ip_manager)

    # Загружаем конфигурацию баз данных
    db_config = load_database_config(env)

    # Определяем список баз для создания
    databases_to_create = []

    if db_type == "all":
        # Собираем все базы из всех категорий
        for db_list in db_config.values():
            if isinstance(db_list, list):
                databases_to_create.extend(db_list)
    elif db_type in db_config:
        databases_to_create = db_config[db_type]
        if not isinstance(databases_to_create, list):
            print(f"Ошибка: конфигурация для типа БД '{db_type}' имеет неверный формат")
            sys.exit(1)
    else:
        print(f"Ошибка: тип БД '{db_type}' не найден в конфигурации для окружения '{env}'")
        print(f"Доступные типы: {', '.join(db_config.keys())}")
        sys.exit(1)

    if not databases_to_create:
        print(f"Нет баз данных для создания в конфигурации '{env}' для типа '{db_type}'")
        sys.exit(1)

    # Подготавливаем список кортежей (name, type, preset_id)
    db_types_cfg = get_database_types_config()
    db_tuples = [
        (
            db["name"],
            db["type"],
            db.get("preset_id", (db_types_cfg.get(db["type"], {}) or {}).get("preset_id")),
        )
        for db in databases_to_create
    ]

    # Получаем настройки бэкапов из конфигурации
    env_config_path = Path(__file__).parent / "config" / "environments" / f"{env}.yaml"
    with open(env_config_path, "r", encoding="utf-8") as f:
        env_config = yaml.safe_load(f)
    auto_backups = env_config.get("auto_backups")

    # Создаем базы данных
    print(f"\nСоздание {len(db_tuples)} {'кластеров' if is_cluster else 'баз данных'}")
    print(f"Тип: {db_type}, Окружение: {env}")
    print("-" * 60)

    try:
        factory.create_multiple(
            databases=db_tuples,
            is_cluster=is_cluster,
            config=config.get("default_config"),
            admin_password=admin_password,
            auto_backups=auto_backups,
        )
        print("\n" + "=" * 60)
        print("✅ Все базы данных успешно созданы!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Ошибка при создании баз данных: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

