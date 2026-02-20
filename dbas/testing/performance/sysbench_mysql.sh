#!/bin/bash
# Тест производительности MySQL с использованием sysbench

# Настройки подключения (можно переопределить через переменные окружения)
MYSQL_HOST="${MYSQL_HOST:-localhost}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
MYSQL_USER="${MYSQL_USER:-gen_user}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:-}"
MYSQL_DB="${MYSQL_DB:-sysbench}"

# Параметры теста (можно переопределить через переменные окружения)
TABLES="${TABLES:-250}"
TABLE_SIZE="${TABLE_SIZE:-100000}"
THREADS="${THREADS:-10}"
DURATION="${DURATION:-300}"
SCRIPT="${SCRIPT:-/usr/share/sysbench/oltp_read_write.lua}"

# Проверка обязательных параметров
if [ -z "$MYSQL_PASSWORD" ]; then
    echo "Ошибка: переменная MYSQL_PASSWORD не установлена"
    exit 1
fi

echo "Настройки подключения:"
echo "  Host: $MYSQL_HOST"
echo "  Port: $MYSQL_PORT"
echo "  User: $MYSQL_USER"
echo "  Database: $MYSQL_DB"
echo ""
echo "Параметры теста:"
echo "  Tables: $TABLES"
echo "  Table size: $TABLE_SIZE"
echo "  Threads: $THREADS"
echo "  Duration: $DURATION"
echo ""

# Подготовка данных
echo "🔧 Подготовка данных..."
sysbench $SCRIPT \
  --mysql-host=$MYSQL_HOST \
  --mysql-port=$MYSQL_PORT \
  --mysql-user=$MYSQL_USER \
  --mysql-password=$MYSQL_PASSWORD \
  --mysql-db=$MYSQL_DB \
  --tables=$TABLES \
  --table-size=$TABLE_SIZE \
  --threads=$THREADS \
  prepare

# Запуск теста
echo "🚀 Запуск теста..."
sysbench $SCRIPT \
  --mysql-host=$MYSQL_HOST \
  --mysql-port=$MYSQL_PORT \
  --mysql-user=$MYSQL_USER \
  --mysql-password=$MYSQL_PASSWORD \
  --mysql-db=$MYSQL_DB \
  --tables=$TABLES \
  --table-size=$TABLE_SIZE \
  --threads=$THREADS \
  --time=$DURATION \
  run

# Очистка данных (раскомментируйте при необходимости)
# echo "🧹 Очистка данных..."
# sysbench $SCRIPT \
#   --mysql-host=$MYSQL_HOST \
#   --mysql-port=$MYSQL_PORT \
#   --mysql-user=$MYSQL_USER \
#   --mysql-password=$MYSQL_PASSWORD \
#   --mysql-db=$MYSQL_DB \
#   --tables=$TABLES \
#   --table-size=$TABLE_SIZE \
#   --threads=$THREADS \
#   cleanup

echo "✅ Готово!"
