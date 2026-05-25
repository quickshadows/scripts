#!/bin/bash

# Настройки подключения
PGSQL_HOST="91.210.170.92"
PGSQL_PORT=5432
PGSQL_USER="gen_user"
PGSQL_PASSWORD='Passwd+++123'
PGSQL_DB="db1"

# Параметры теста
TABLES=10
TABLE_SIZE=1000000
THREADS=3
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
