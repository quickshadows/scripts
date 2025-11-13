#!/usr/bin/env python3
import os
import sys
import time
import json
import requests

# ==========================
# Настройки
# ==========================
TIMEWEB_CLOUD_TOKEN = os.getenv("TIMEWEB_CLOUD_TOKEN")
if not TIMEWEB_CLOUD_TOKEN:
    print("Ошибка: переменная окружения TIMEWEB_CLOUD_TOKEN не установлена.")
    sys.exit(1)

NETWORK_ID = "network-3654798e575f4dd3b9ad3e9dec940ead"
PROJECT_ID = 103757
AVAILABILITY_ZONE = "spb-3"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TIMEWEB_CLOUD_TOKEN}"
}

# ==========================
# Базы данных
# ==========================
databases_pg = [
    ("PostgreSQL 14 api prod", "postgres14", 1175),
    ("PostgreSQL 15 api prod", "postgres15", 1175),
    ("PostgreSQL 16 api prod", "postgres16", 1175),
    ("PostgreSQL 17 api prod", "postgres17", 1175),
    ("PostgreSQL 18 api prod", "postgres18", 1175)
]

databases_mysql = [
    ("MySQL 8.0 api prod", "mysql", 519),
    ("MySQL 8.4 api prod", "mysql8_4", 519)
]

# ==========================
# Функции
# ==========================
def get_floating_ip():
    """Создает новый плавающий IP."""
    url = "https://timeweb.cloud/api/v1/floating-ips"
    payload = {
        "is_ddos_guard": False,
        "availability_zone": AVAILABILITY_ZONE
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    data = response.json()

    floating_ip = data.get("ip", {}).get("ip")
    if not floating_ip:
        print("Ошибка: Не удалось получить плавающий IP.")
        print("Ответ API:", json.dumps(data, indent=2, ensure_ascii=False))
        sys.exit(1)

    time.sleep(1)
    return floating_ip


def get_busy_ips():
    """Получает список занятых IP-адресов."""
    url = f"https://api.timeweb.cloud/api/v2/vpcs/{NETWORK_ID}"
    response = requests.get(url, headers=HEADERS)
    data = response.json()

    busy_ips = data.get("vpc", {}).get("busy_address")
    if not busy_ips:
        print("Ошибка: Не удалось получить занятые IP-адреса.")
        sys.exit(1)

    return busy_ips


def find_first_free_ip():
    """Находит первый свободный приватный IP из диапазона 192.168.0.2–254."""
    busy_ips = get_busy_ips()
    for i in range(2, 255):
        ip = f"192.168.0.{i}"
        if ip not in busy_ips:
            return ip
    return None


def create_database(db_name, db_type, preset_id, local_ip, floating_ip, is_cluster=False):
    """Создает базу данных через API."""
    url = "https://timeweb.cloud/api/v1/databases"

    payload = {
        "name": db_name,
        "type": db_type,
        "configuration": {
            "configurator_id": 45,
            "cpu": 1,
            "ram": 1024,
            "disk": 10240
        },
        "availability_zone": AVAILABILITY_ZONE,
        "hash_type": "caching_sha2",
        "project_id": PROJECT_ID,
        "admin": {
            "password": "Passwd123",
            "for_all": False
        },
        "network": {
            "id": NETWORK_ID,
            "floating_ip": floating_ip,
            "local_ip": local_ip
        }
    }

    if is_cluster:
        payload["replication"] = {"count": 3}

    response = requests.post(url, headers=HEADERS, json=payload)
    data = response.json()

    print(f"\nОтвет API на создание {'кластера' if is_cluster else 'базы'} '{db_name}':")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    time.sleep(2)


# ==========================
# Меню
# ==========================
def show_menu():
    print("\nВыберите вариант создания баз данных:\n")
    print("1 — Только PostgreSQL (single)")
    print("2 — Только MySQL (single)")
    print("3 — Все базы (single)")
    print("4 — Только PostgreSQL (cluster)")
    print("5 — Только MySQL (cluster)")
    print("6 — Все базы (cluster)")
    print("0 — Выход")

    choice = input("\nВаш выбор: ").strip()
    return choice


# ==========================
# Основной цикл
# ==========================
def main():
    choice = show_menu()

    if choice == "0":
        print("Выход.")
        sys.exit(0)

    # Определяем набор баз и флаг кластера
    if choice == "1":
        selected_dbs = databases_pg
        is_cluster = False
    elif choice == "2":
        selected_dbs = databases_mysql
        is_cluster = False
    elif choice == "3":
        selected_dbs = databases_pg + databases_mysql
        is_cluster = False
    elif choice == "4":
        selected_dbs = databases_pg
        is_cluster = True
    elif choice == "5":
        selected_dbs = databases_mysql
        is_cluster = True
    elif choice == "6":
        selected_dbs = databases_pg + databases_mysql
        is_cluster = True
    else:
        print("Неверный выбор.")
        sys.exit(1)

    # Создание баз
    for db_name, db_type, preset_id in selected_dbs:
        floating_ip = get_floating_ip()
        local_ip = find_first_free_ip()

        if not local_ip:
            print(f"Ошибка: нет свободного приватного IP для {db_name}")
            sys.exit(1)

        print(f"\nСоздание {'кластера' if is_cluster else 'базы'} {db_name} ({db_type})")
        print(f"floating IP: {floating_ip}, local IP: {local_ip}")

        create_database(db_name, db_type, preset_id, local_ip, floating_ip, is_cluster=is_cluster)


if __name__ == "__main__":
    main()
