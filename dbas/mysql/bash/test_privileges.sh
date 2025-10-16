#!/bin/bash
read -rp "Введите хост PostgreSQL: " MYSQLHOST

if [[ -n "$TOKEN" ]]; then
  echo "TOKEN задан"
else
  read -ro "Введите token: " TOKEN
  export TOKEN="$TOKEN"
fi

MYSQLUSER="gen_user"
MYSQLUSER1="user"
MYSQLPASSWORD="Pass"
MYSQLPORT="5432"
MYSQLDATABASE="default_db"

DB_ID=$(twc db list | egrep "$MYSQLHOST" | awk 'print $1')
INSTANCE_ID=$(twc db instance list $DB_ID | egrep "$MYSQLDATABASE")

twc db user create $DB_ID --login "$MYSQLUSER1" --password "$MYSQLPASSWORD" --privileges ""

#Массив id юзеров
readarray -t ID_USERS < <(twc db user ls "$DB_ID" | awk 'NR > 1 { print $1 }')

# Временный файл для SQL
TMP_SQL=$(mktemp)

# Установим пароль
export MYSQLPASSWORD="$MYSQLPASSWORD"

### Проверка с основного пользователя.
function test_query_from_gen_user() {
    local label="$1"
    local sql="$2"

    echo "$sql" > "$TMP_SQL"

    local output
    output=$(mysql -u "$MYSQLUSER" -h "$MYSQLHOST" -P "$MYSQLPORT" "$MYSQLDATABASE" < "$TMP_SQL")

    if [[ $? -eq 0 ]]; then
        echo "gen_user [PASS] $label"
    else
        echo "gen_user [FAIL] $label"
        echo "--- ERROR ---"
        echo "$output"
    fi
}

### Проверка с дополнительного пользователя.
# function test_query_from_user() {
#     local label="$1"
#     local sql="$2"

#     echo "$sql" > "$TMP_SQL"

#     local output
#     output=$(psql -U "$MYSQLUSER1" -h "$MYSQLHOST" -p "$MYSQLPORT" -d "$MYSQLDATABASE" -f "$TMP_SQL" -v ON_ERROR_STOP=1 2>&1)

#     if [[ $? -eq 0 ]]; then
#         echo "user [PASS] $label"
#     else
#         echo "user [FAIL] $label"
#         echo "--- ERROR ---"
#         echo "$output"
#     fi
# }

function on_prava() {
for ID_USER in "${ID_USERS[@]}"; do
curl "https://timeweb.cloud/api/v1/databases/${DB_ID}/admins/${ID_USER}" \
  -X 'PATCH' \
  -H 'content-type: application/json' \
  -H "authorization: Bearer ${TOKEN}" \
  --data-raw '{"privileges":["INSERT","UPDATE","DELETE","CREATE","TRUNCATE","REFERENCES","TRIGGER","TEMPORARY","CREATEDB"],"instance_id":'"${INSTANCE_ID}"',"for_all":false}' > /dev/null 2>&1
#  echo -e "\n✔ Пользователь $ID_USER обработан"
  done

  for ID_USER in "${ID_USERS[@]}"; do
curl "https://timeweb.cloud/api/v1/databases/${DB_ID}/admins/${ID_USER}" \
  -X 'PATCH' \
  -H 'content-type: application/json' \
  -H "authorization: Bearer ${TOKEN}" \
  --data-raw '{"privileges":["CREATE_DB","CREATE","INSERT","SELECT","UPDATE","DELETE","CREATE_VIEW","SHOW_VIEW","INDEX","ALTER","LOCK_TABLES","REFERENCES","TRIGGER","CREATE_ROUTINE","ALTER_ROUTINE","CREATE_TEMPORARY_TABLES","EVENT","DROP","CREATE_USER","PROCESS","SLOW_LOG"],"instance_id":'"${INSTANCE_ID}"',"for_all":false}' > /dev/null 2>&1
#  echo -e "\n✔ Пользователь $ID_USER обработан"
done
  sleep 60
}

#сбрасываем права
function off_prava () {
for ID_USER in "${ID_USERS[@]}"; do
curl "https://timeweb.cloud/api/v1/databases/${DB_ID}/admins/${ID_USER}" \
  -X 'PATCH' \
  -H 'content-type: application/json' \
  -H "authorization: Bearer ${TOKEN}" \
  --data-raw '{"privileges":[],"instance_id":'"${INSTANCE_ID}"',"for_all":false}'
  echo -e "\n✔ Пользователь $ID_USER обработан"
#  echo "URL: https://timeweb.cloud/api/v1/databases/${DB_ID}/admins/${ID_USER}"

done

sleep 60
}

off_prava
#CREATE_DB

test_query_from_gen_user "CREATE" "CREATE DATABASE test_privs;"
# CREATE
test_query_from_gen_user "CREATE" "CREATE TABLE test_table (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  value INT
);"

# INSERT
test_query_from_user "INSERT" "SELECT * FROM test_table;"

# SELECT
test_query_from_user "SELECT" "SELECT * FROM test_table;"

# UPDATE
test_query_from_user "UPDATE" "UPDATE test_table SET value = 99 WHERE name = 'alpha';"

#DELETE
test_query_from_user "DELETE" "DELETE FROM test_table WHERE name = 'beta';"

#CREATE_VIEW
test_query_from_user "CREATE_VIEW" "CREATE VIEW test_view AS SELECT id, name FROM test_table;"

# SHOW_VIEW
test_query_from_gen_user "SHOW_VIEW" "SHOW CREATE VIEW test_view;"

test_query_from_user "INDEX" "DROP INDEX idx_value ON test_table(valye); DROP INDEX idx_value ON test_table;"

test_query_from_gen_user "ALTER" "ALTER TABLE test_table ADD COLUMN updated_at TIMESTAMP NULL;"

# LOCK_TABLES
test_query_from_user "LOCK_TABLES" "LOCK TABLES test_table READ; UNLOCK TABLES;"

# REFERENCES
test_query_from_user "REFERENCES" "CREATE TABLE ref_table (
  id INT PRIMARY KEY,
  test_id INT,
  FOREIGN KEY (test_id) REFERENCES test_table(id)
);
DROP TABLE ref_table;"

#TRIGGER
test_query_from_gen_user "TRIGGER" "CREATE TRIGGER trg_before_insert
BEFORE INSERT ON test_table
FOR EACH ROW
SET @trigger_fired = 1;
DROP TRIGGER trg_before_insert;
"
#CREATE_ROUTINE
test_query_from_gen_user "CREATE_ROUTINE" "DELIMITER //
CREATE PROCEDURE test_proc()
BEGIN
  SELECT 'routine works' AS result;
END //
DELIMITER ;
"

#ALTER_ROUTINE
test_query_from_gen_user "ALTER_ROUTINE" "ALTER PROCEDURE test_proc COMMENT 'modified';"

#CREATE_TEMPORARY_TABLES
test_query_from_gen_user "CREATE_TEMPORARY_TABLES" "CREATE TEMPORARY TABLE tmp_table (id INT);
INSERT INTO tmp_table VALUES (1);
SELECT * FROM tmp_table;"

#EVENT
test_query_from_gen_user "EVENT" "CREATE EVENT test_event
ON SCHEDULE AT CURRENT_TIMESTAMP + INTERVAL 1 MINUTE
DO INSERT INTO test_table (name, value) VALUES ('event_test', 1);
DROP EVENT test_event;"

#DROP
test_query_from_gen_user "DROP" "DROP VIEW test_view;
DROP TABLE test_table;"

#CREATE_USER
test_query_from_gen_user "CREATE_USER" "CREATE USER 'tmp_user'@'localhost' IDENTIFIED BY 'test123';
DROP USER 'tmp_user'@'localhost';"

#PROCESS
test_query_from_gen_user "PROCESS" "SHOW PROCESSLIST;"

#SLOW_LOG
test_query_from_gen_user "SLOW_LOG" "SELECT * FROM mysql.slow_log LIMIT 5;"



#Включаем все права
for ID_USER in "${ID_USERS[@]}"; do
curl "https://timeweb.cloud/api/v1/databases/${DB_ID}/admins/${ID_USER}" \
  -X 'PATCH' \
  -H 'content-type: application/json' \
  -H "authorization: Bearer ${TOKEN}" \
  --data-raw '{"privileges":["SELECT","INSERT","UPDATE","DELETE","CREATE","TRUNCATE","REFERENCES","TRIGGER","TEMPORARY","CREATEDB"],"instance_id":'"${INSTANCE_ID}"',"for_all":false}'
  echo -e "\n✔ Пользователь $ID_USER обработан"
#  echo "URL: https://timeweb.cloud/api/v1/databases/${DB_ID}/admins/${ID_USER}"

done

sleep 90

test_query_from_gen_user "CREATE" "CREATE DATABASE test_privs;"
# CREATE
test_query_from_gen_user "CREATE" "CREATE TABLE test_table (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  value INT
);"

# INSERT
test_query_from_user "INSERT" "SELECT * FROM test_table;"

# SELECT
test_query_from_user "SELECT" "SELECT * FROM test_table;"

# UPDATE
test_query_from_user "UPDATE" "UPDATE test_table SET value = 99 WHERE name = 'alpha';"

#DELETE
test_query_from_user "DELETE" "DELETE FROM test_table WHERE name = 'beta';"

#CREATE_VIEW
test_query_from_user "CREATE_VIEW" "CREATE VIEW test_view AS SELECT id, name FROM test_table;"

# SHOW_VIEW
test_query_from_gen_user "SHOW_VIEW" "SHOW CREATE VIEW test_view;"

test_query_from_user "INDEX" "DROP INDEX idx_value ON test_table(valye); DROP INDEX idx_value ON test_table;"

test_query_from_gen_user "ALTER" "ALTER TABLE test_table ADD COLUMN updated_at TIMESTAMP NULL;"

# LOCK_TABLES
test_query_from_user "LOCK_TABLES" "LOCK TABLES test_table READ; UNLOCK TABLES;"

# REFERENCES
test_query_from_user "REFERENCES" "CREATE TABLE ref_table (
  id INT PRIMARY KEY,
  test_id INT,
  FOREIGN KEY (test_id) REFERENCES test_table(id)
);
DROP TABLE ref_table;"

#TRIGGER
test_query_from_gen_user "TRIGGER" "CREATE TRIGGER trg_before_insert
BEFORE INSERT ON test_table
FOR EACH ROW
SET @trigger_fired = 1;
DROP TRIGGER trg_before_insert;
"
#CREATE_ROUTINE
test_query_from_gen_user "CREATE_ROUTINE" "DELIMITER //
CREATE PROCEDURE test_proc()
BEGIN
  SELECT 'routine works' AS result;
END //
DELIMITER ;
"

#ALTER_ROUTINE
test_query_from_gen_user "ALTER_ROUTINE" "ALTER PROCEDURE test_proc COMMENT 'modified';"

#CREATE_TEMPORARY_TABLES
test_query_from_gen_user "CREATE_TEMPORARY_TABLES" "CREATE TEMPORARY TABLE tmp_table (id INT);
INSERT INTO tmp_table VALUES (1);
SELECT * FROM tmp_table;"

#EVENT
test_query_from_gen_user "EVENT" "CREATE EVENT test_event
ON SCHEDULE AT CURRENT_TIMESTAMP + INTERVAL 1 MINUTE
DO INSERT INTO test_table (name, value) VALUES ('event_test', 1);
DROP EVENT test_event;"

#DROP
test_query_from_gen_user "DROP" "DROP VIEW test_view;
DROP TABLE test_table;"

#CREATE_USER
test_query_from_gen_user "CREATE_USER" "CREATE USER 'tmp_user'@'localhost' IDENTIFIED BY 'test123';
DROP USER 'tmp_user'@'localhost';"

#PROCESS
test_query_from_gen_user "PROCESS" "SHOW PROCESSLIST;"

#SLOW_LOG
test_query_from_gen_user "SLOW_LOG" "SELECT * FROM mysql.slow_log LIMIT 5;"


# Очистка
rm "$TMP_SQL"
