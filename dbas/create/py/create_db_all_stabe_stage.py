#!/usr/bin/env python3

import os
import sys
import time
import json
from dataclasses import dataclass
from typing import List

import requests

# =========================================================
# Конфиг
# =========================================================

API_URL = "https://cloud-staging.kube.timeweb.net/api/v1"
VPC_API_URL = "https://api.timeweb.cloud/api/v2"

TIMEWEB_CLOUD_TOKEN = os.getenv("TIMEWEB_CLOUD_TOKEN")

if not TIMEWEB_CLOUD_TOKEN:
    print("Ошибка: TIMEWEB_CLOUD_TOKEN не установлен")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {TIMEWEB_CLOUD_TOKEN}",
    "Content-Type": "application/json",
}

NETWORK_ID = "network-21aaf7144ced4dabac9ae7c52db60ea9"
PROJECT_ID = 103757
AVAILABILITY_ZONE = "fra-1"

CONFIGURATOR_ID = {
    "fra-1": 83,
    "spb-1": 45,
    "ams-1": 50,
}

ADMIN_PASSWORD = "Passwd+++123"

# =========================================================
# Модели
# =========================================================

@dataclass
class DatabaseConfig:
    name: str
    db_type: str
    preset_id: int = 0


# =========================================================
# Базы
# =========================================================

DATABASE_GROUPS = {
    "postgres": [
        DatabaseConfig("PostgreSQL 14 api-stage-patroni-14", "postgres14"),
        DatabaseConfig("PostgreSQL 15 api-stage-patroni-14", "postgres15"),
        DatabaseConfig("PostgreSQL 16 api-stage-patroni-14", "postgres16"),
        DatabaseConfig("PostgreSQL 17 api-stage-patroni-14", "postgres17"),
        DatabaseConfig("PostgreSQL 18 api-stage-patroni-14", "postgres18"),
    ],
    "mysql": [
        DatabaseConfig("MySQL 8.0 api-stage-watcher-14", "mysql"),
        # DatabaseConfig("MySQL 8.4 api-stage-watcher-14", "mysql8_4"),
    ],
    "redis": [
        DatabaseConfig("Redis 7 api-stage", "redis7"),
        DatabaseConfig("Redis 8.1 api-stage", "redis8_1"),
    ],
    "mongodb": [
        DatabaseConfig("MongoDB 7 api-stage", "mongodb7"),
        DatabaseConfig("MongoDB 8.0 api-stage", "mongodb8_0"),
    ],
    "opensearch": [
        DatabaseConfig("OpenSearch 2.19.1 api-stspb-manager03", "opensearch2_19"),
    ],
    "clickhouse": [
        DatabaseConfig("ClickHouse 23.10.1 api-stage", "clickhouse"),
        DatabaseConfig("ClickHouse 24.8.14 api-stage", "clickhouse24"),
        DatabaseConfig("ClickHouse 25.1.6 api-stage", "clickhouse25"),
    ],
    "kafka": [
        DatabaseConfig("Kafka 3.5.1 api-stspb-manager03", "kafka"),
    ],
    "rabbitmq": [
        DatabaseConfig("RabbitMQ 4.0 api-stspb-manager03", "rabbitmq4_0"),
    ],
}

# =========================================================
# API
# =========================================================

def api_request(method: str, url: str, **kwargs):
    response = requests.request(method, url, headers=HEADERS, timeout=30, **kwargs)

    try:
        data = response.json()
    except Exception:
        print("Ошибка JSON:")
        print(response.text)
        sys.exit(1)

    if response.status_code >= 400:
        print(f"HTTP {response.status_code}")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        sys.exit(1)

    return data


# =========================================================
# Floating IP
# =========================================================

def create_floating_ip() -> str:
    payload = {
        "is_ddos_guard": False,
        "availability_zone": AVAILABILITY_ZONE,
    }

    data = api_request(
        "POST",
        f"{API_URL}/floating-ips",
        json=payload,
    )

    ip = data.get("ip", {}).get("ip")

    if not ip:
        print("Не удалось получить floating IP")
        sys.exit(1)

    print(f"[+] Floating IP: {ip}")

    time.sleep(1)

    return ip


# =========================================================
# Local IP
# =========================================================

def get_busy_ips() -> List[str]:
    data = api_request(
        "GET",
        f"{VPC_API_URL}/vpcs/{NETWORK_ID}",
    )

    return data.get("vpc", {}).get("busy_address", [])


def get_free_local_ip() -> str:
    busy_ips = get_busy_ips()

    for i in range(2, 255):
        ip = f"192.168.0.{i}"

        if ip not in busy_ips:
            return ip

    raise RuntimeError("Нет свободных локальных IP")


# =========================================================
# Payload
# =========================================================

def build_payload(
    db: DatabaseConfig,
    local_ip: str,
    floating_ip: str,
    cluster: bool = False,
    heavy: bool = False,
):
    payload = {
        "name": db.name,
        "type": db.db_type,
        "project_id": PROJECT_ID,
        "availability_zone": AVAILABILITY_ZONE,
        "hash_type": "caching_sha2",
        "configuration": {
            "configurator_id": CONFIGURATOR_ID[AVAILABILITY_ZONE],
            "cpu": 2,
            "ram": 2048,
            "disk": 20480,
        },
        "admin": {
            "password": ADMIN_PASSWORD,
            "for_all": False,
        },
        "network": {
            "id": NETWORK_ID,
            "floating_ip": floating_ip,
            "local_ip": local_ip,
        },
        "auto_backups": {
            "copy_count": 1,
            "creation_start_at": "2025-12-03T15:03:55.704Z",
            "interval": "day",
            "day_of_week": 3,
        },
    }

    if cluster:
        payload["name"] += "_cl"
        payload["replication"] = {
            "count": 3
        }

    if heavy:
        payload["configuration"] = {
            "configurator_id": CONFIGURATOR_ID[AVAILABILITY_ZONE],
            "cpu": 4,
            "ram": 8192,
            "disk": 20480,
        }

    return payload


# =========================================================
# Создание БД
# =========================================================

def create_database(
    db: DatabaseConfig,
    cluster: bool = False,
    heavy: bool = False,
):
    print("=" * 60)
    print(f"Создание: {db.name}")

    floating_ip = create_floating_ip()
    local_ip = get_free_local_ip()

    print(f"[+] Local IP:    {local_ip}")
    print(f"[+] Floating IP: {floating_ip}")

    payload = build_payload(
        db=db,
        local_ip=local_ip,
        floating_ip=floating_ip,
        cluster=cluster,
        heavy=heavy,
    )

    data = api_request(
        "POST",
        f"{API_URL}/databases",
        json=payload,
    )

    print("\nУспешно создано:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    time.sleep(2)


# =========================================================
# Меню
# =========================================================

MENU = {
    "1": {
        "title": "PostgreSQL single",
        "dbs": DATABASE_GROUPS["postgres"],
        "cluster": False,
        "heavy": False,
    },
    "2": {
        "title": "MySQL single",
        "dbs": DATABASE_GROUPS["mysql"],
        "cluster": False,
        "heavy": False,
    },
    "3": {
        "title": "Все основные single",
        "dbs": DATABASE_GROUPS["postgres"] + DATABASE_GROUPS["mysql"],
        "cluster": False,
        "heavy": False,
    },
    "4": {
        "title": "PostgreSQL cluster",
        "dbs": DATABASE_GROUPS["postgres"],
        "cluster": True,
        "heavy": False,
    },
    "5": {
        "title": "MySQL cluster",
        "dbs": DATABASE_GROUPS["mysql"],
        "cluster": True,
        "heavy": False,
    },
    "6": {
        "title": "Все основные cluster",
        "dbs": DATABASE_GROUPS["postgres"] + DATABASE_GROUPS["mysql"],
        "cluster": True,
        "heavy": False,
    },
    "7": {
        "title": "Тяжелые DBaaS",
        "dbs": (
            DATABASE_GROUPS["opensearch"]
            + DATABASE_GROUPS["clickhouse"]
            + DATABASE_GROUPS["kafka"]
            + DATABASE_GROUPS["rabbitmq"]
        ),
        "cluster": False,
        "heavy": True,
    },
    "8": {
        "title": "Легкие DBaaS",
        "dbs": (
            DATABASE_GROUPS["redis"]
            + DATABASE_GROUPS["mongodb"]
        ),
        "cluster": False,
        "heavy": False,
    },
}


def show_menu():
    print("\nВыберите режим:\n")

    for key, item in MENU.items():
        print(f"{key} — {item['title']}")

    print("0 — Выход")

    return input("\nВаш выбор: ").strip()


# =========================================================
# Main
# =========================================================

def main():
    choice = show_menu()

    if choice == "0":
        print("Выход")
        return

    selected = MENU.get(choice)

    if not selected:
        print("Неверный выбор")
        sys.exit(1)

    print(f"\nЗапуск режима: {selected['title']}")

    for db in selected["dbs"]:
        try:
            create_database(
                db=db,
                cluster=selected["cluster"],
                heavy=selected["heavy"],
            )
        except Exception as e:
            print(f"\nОшибка при создании {db.name}")
            print(e)


if __name__ == "__main__":
    main()