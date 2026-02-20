#!/bin/bash

# Настройки подключения
PGSQL_HOST="81.200.153.5"
PGSQL_PORT=5432
PGSQL_USER="gen_user"
PGSQL_PASSWORD='c6=;t}(D^jSa,w'
PGSQL_DB="sysbench"

# Параметры теста
TABLES=50
TABLE_SIZE=1000000
THREADS=8
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
#echo "🚀 Запуск теста..."
#sysbench --db-driver=pgsql $SCRIPT \
#  --pgsql-host=$PGSQL_HOST \
#  --pgsql-port=$PGSQL_PORT \
#  --pgsql-user=$PGSQL_USER \
#  --pgsql-password=$PGSQL_PASSWORD \
#  --pgsql-db=$PGSQL_DB \
#  --tables=$TABLES \
#  --table-size=$TABLE_SIZE \
#  --threads=$THREADS \
#  --time=$DURATION \
#  run

# Очистка
#echo "🧹 Очистка данных..."
#sysbench --db-driver=pgsql $SCRIPT \
#  --pgsql-host=$PGSQL_HOST \
#  --pgsql-port=$PGSQL_PORT \
#  --pgsql-user=$PGSQL_USER \
#  --pgsql-password=$PGSQL_PASSWORD \
#  --pgsql-db=$PGSQL_DB \
#  --tables=$TABLES \
#  --table-size=$TABLE_SIZE \
#  --threads=$THREADS \
#  cleanup

echo "✅ Готово!"
