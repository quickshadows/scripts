#!/usr/bin/env python3

import argparse
import concurrent.futures
import socket

import psycopg2
import pymysql


# =========================
# CONFIG
# =========================

DB_USER = "gen_user"
DB_PASS = "Passwd+++123"
DB_NAME = "default_db"

POSTGRES_PORT = 5432
MYSQL_PORT = 3306

CONNECT_TIMEOUT = 5
MAX_WORKERS = 20


# =========================
# SQL
# =========================

POSTGRES_SQL = """
CREATE TABLE IF NOT EXISTS test_table_1 (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    value TEXT
);

CREATE TABLE IF NOT EXISTS test_table_2 (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    value TEXT
);

CREATE TABLE IF NOT EXISTS test_table_3 (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    value TEXT
);

CREATE TABLE IF NOT EXISTS test_table_4 (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    value TEXT
);

CREATE TABLE IF NOT EXISTS test_table_5 (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    value TEXT
);
"""


MYSQL_SQL = """
CREATE TABLE IF NOT EXISTS test_table_1 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    value TEXT
);

CREATE TABLE IF NOT EXISTS test_table_2 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    value TEXT
);

CREATE TABLE IF NOT EXISTS test_table_3 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    value TEXT
);

CREATE TABLE IF NOT EXISTS test_table_4 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    value TEXT
);

CREATE TABLE IF NOT EXISTS test_table_5 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    value TEXT
);
"""


# =========================
# FUNCTIONS
# =========================

def create_postgres(ip: str):
    conn = psycopg2.connect(
        host=ip,
        port=POSTGRES_PORT,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME,
        connect_timeout=CONNECT_TIMEOUT,
    )

    conn.autocommit = True

    with conn.cursor() as cur:
        cur.execute(POSTGRES_SQL)

    conn.close()


def create_mysql(ip: str):
    conn = pymysql.connect(
        host=ip,
        port=MYSQL_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        connect_timeout=CONNECT_TIMEOUT,
        autocommit=True,
        ssl={"ssl": {}}
    )

    with conn.cursor() as cur:
        for statement in MYSQL_SQL.split(";"):
            statement = statement.strip()

            if statement:
                cur.execute(statement)

    conn.close()


def worker(db_type: str, ip: str):
    try:
        socket.setdefaulttimeout(CONNECT_TIMEOUT)

        if db_type == "postgres":
            create_postgres(ip)

        elif db_type == "mysql":
            create_mysql(ip)

        else:
            return f"[{ip}] UNKNOWN DB TYPE"

        return f"[{ip}] OK"

    except Exception as e:
        return f"[{ip}] ERROR: {e}"


# =========================
# MAIN
# =========================

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-type",
        required=True,
        choices=["postgres", "mysql"],
        help="Database type",
    )

    parser.add_argument(
        "ips",
        nargs="+",
        help="List of IP addresses",
    )

    args = parser.parse_args()

    print(f"DB type: {args.type}")
    print(f"Total IPs: {len(args.ips)}")
    print()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = [
            executor.submit(worker, args.type, ip)
            for ip in args.ips
        ]

        for future in concurrent.futures.as_completed(futures):
            print(future.result())


if __name__ == "__main__":
    main()
