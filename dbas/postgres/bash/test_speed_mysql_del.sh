#!/bin/bash

# Настройки подключения
PGSQL_HOST="45.153.70.181"
PGSQL_PORT=5432
PGSQL_USER="gen_user"
PGSQL_PASSWORD='Passwd123'
PGSQL_DB="db1"

# Параметры теста
TABLES=8
TABLE_SIZE=10000
THREADS=8
DURATION=60
SCRIPT="/usr/share/sysbench/oltp_read_write.lua"

# Очистка
echo "🧹 Очистка данных..."
sysbench --db-driver=pgsql $SCRIPT \
  --pgsql-host=$PGSQL_HOST \
  --pgsql-port=$PGSQL_PORT \
  --pgsql-user=$PGSQL_USER \
  --pgsql-password=$PGSQL_PASSWORD \
  --pgsql-db=$PGSQL_DB \
  --tables=$TABLES \
  --table-size=$TABLE_SIZE \
  --threads=$THREADS \
  cleanup

echo "✅ Готово!"
