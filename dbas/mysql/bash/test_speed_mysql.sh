#!/bin/bash

# Настройки подключения
MYSQL_HOST="46.19.67.214"
MYSQL_PORT=3306
MYSQL_USER="gen_user"
MYSQL_PASSWORD='Passwd123'
MYSQL_DB="db1"

# Параметры теста
TABLES=250
TABLE_SIZE=100000
THREADS=10
DURATION=300
SCRIPT="/usr/share/sysbench/oltp_read_write.lua"

# # Подготовка
echo $MYSQL_HOST
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
# echo "🚀 Запуск теста..."
# sysbench $SCRIPT \
#   --mysql-host=$MYSQL_HOST \
#   --mysql-port=$MYSQL_PORT \
#   --mysql-user=$MYSQL_USER \
#   --mysql-password=$MYSQL_PASSWORD \
#   --mysql-db=$MYSQL_DB \
#   --tables=$TABLES \
#   --table-size=$TABLE_SIZE \
#   --threads=$THREADS \
#   --time=$DURATION \
#   run

# Очистка
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
