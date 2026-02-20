#!/bin/bash
# Тест производительности PostgreSQL с использованием sysbench

# Настройки подключения (можно переопределить через переменные окружения)
PGSQL_HOST="${PGSQL_HOST:-localhost}"
PGSQL_PORT="${PGSQL_PORT:-5432}"
PGSQL_USER="${PGSQL_USER:-gen_user}"
PGSQL_PASSWORD="${PGSQL_PASSWORD:-}"
PGSQL_DB="${PGSQL_DB:-sysbench}"

# Параметры теста (можно переопределить через переменные окружения)
TABLES="${TABLES:-50}"
TABLE_SIZE="${TABLE_SIZE:-1000000}"
THREADS="${THREADS:-8}"
DURATION="${DURATION:-60}"
SCRIPT="${SCRIPT:-/usr/share/sysbench/oltp_read_write.lua}"

# Проверка обязательных параметров
if [ -z "$PGSQL_PASSWORD" ]; then
    echo "Ошибка: переменная PGSQL_PASSWORD не установлена"
    exit 1
fi

echo "Настройки подключения:"
echo "  Host: $PGSQL_HOST"
echo "  Port: $PGSQL_PORT"
echo "  User: $PGSQL_USER"
echo "  Database: $PGSQL_DB"
echo ""
echo "Параметры теста:"
echo "  Tables: $TABLES"
echo "  Table size: $TABLE_SIZE"
echo "  Threads: $THREADS"
echo "  Duration: $DURATION"
echo ""

# Подготовка данных
echo "🔧 Подготовка данных..."
sysbench --db-driver=pgsql $SCRIPT \
  --pgsql-host=$PGSQL_HOST \
  --pgsql-port=$PGSQL_PORT \
  --pgsql-user=$PGSQL_USER \
  --pgsql-password=$PGSQL_PASSWORD \
  --pgsql-db=$PGSQL_DB \
  --tables=$TABLES \
  --threads=$THREADS \
  --table-size=$TABLE_SIZE \
  prepare

# Запуск теста
echo "🚀 Запуск теста..."
sysbench --db-driver=pgsql $SCRIPT \
  --pgsql-host=$PGSQL_HOST \
  --pgsql-port=$PGSQL_PORT \
  --pgsql-user=$PGSQL_USER \
  --pgsql-password=$PGSQL_PASSWORD \
  --pgsql-db=$PGSQL_DB \
  --tables=$TABLES \
  --table-size=$TABLE_SIZE \
  --threads=$THREADS \
  --time=$DURATION \
  run

# Очистка данных (раскомментируйте при необходимости)
# echo "🧹 Очистка данных..."
# sysbench --db-driver=pgsql $SCRIPT \
#   --pgsql-host=$PGSQL_HOST \
#   --pgsql-port=$PGSQL_PORT \
#   --pgsql-user=$PGSQL_USER \
#   --pgsql-password=$PGSQL_PASSWORD \
#   --pgsql-db=$PGSQL_DB \
#   --tables=$TABLES \
#   --table-size=$TABLE_SIZE \
#   --threads=$THREADS \
#   cleanup

echo "✅ Готово!"
