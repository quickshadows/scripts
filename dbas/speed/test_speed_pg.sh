#!/bin/bash

# Настройки подключения
PGSQL_HOST="89.23.98.204"
PGSQL_PORT=5432
PGSQL_USER="gen_user"
PGSQL_PASSWORD='Pass'
PGSQL_DB="default_db"

# Параметры теста
TABLES=60
TABLE_SIZE=1000000
THREADS=6
DURATION=60
SCRIPT="/usr/share/sysbench/oltp_read_write.lua"

# Подготовка
echo $PGSQL_HOST
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
# echo "🚀 Запуск теста..."
# sysbench --db-driver=pgsql $SCRIPT \
#   --pgsql-host=$PGSQL_HOST \
#   --pgsql-port=$PGSQL_PORT \
#   --pgsql-user=$PGSQL_USER \
#   --pgsql-password=$PGSQL_PASSWORD \
#   --pgsql-db=$PGSQL_DB \
#   --tables=$TABLES \
#   --table-size=$TABLE_SIZE \
#   --threads=$THREADS \
#   --time=$DURATION \
#   run

# Очистка
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
