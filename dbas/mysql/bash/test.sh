#!/bin/bash
#read -rp "Введите хост PostgreSQL: " MYSQLHOST

if [[ -n "$TOKEN" ]]; then
  echo "TOKEN задан"
else
  read -ro "Введите token: " TOKEN
  export TOKEN="$TOKEN"
fi

MYSQLHOST="147.45.212.3"
MYSQLUSER="gen_user"
MYSQLUSER1="user"
MYSQLPASSWORD="pass"
MYSQLPORT="3306"
MYSQLDATABASE="default_db"

DB_ID=$(twc db list | egrep "$MYSQLHOST" | awk '{print $1}')
INSTANCE_ID=$(twc db instance list $DB_ID | egrep "$MYSQLDATABASE" | awk '{print $1}')

# twc db user create $DB_ID --login "$MYSQLUSER1" --password "$MYSQLPASSWORD" --privileges ""

#Массив id юзеров
readarray -t ID_USERS < <(twc db user ls "$DB_ID" | awk 'NR > 1 {print $1}')

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
    output=$(mysql -u "$MYSQLUSER" -h "$MYSQLHOST" -P "$MYSQLPORT" -p"$MYSQLPASSWORD" "$MYSQLDATABASE" < "$TMP_SQL")

    echo "mysql -u "$MYSQLUSER" -h "$MYSQLHOST" -P "$MYSQLPORT" -p"$MYSQLPASSWORD" "$MYSQLDATABASE" < "$sql""

    if [[ $? -eq 0 ]]; then
        echo "gen_user [PASS] $label"
    else
        echo "gen_user [FAIL] $label"
        echo "--- ERROR ---"
        echo "$output"
    fi
}

function on_prava() {
for ID_USER in "${ID_USERS[@]}"; do
curl "https://timeweb.cloud/api/v1/databases/${DB_ID}/admins/${ID_USER}" \
  -X 'PATCH' \
  -H 'content-type: application/json' \
  -H "authorization: Bearer ${TOKEN}" \
  --data-raw '{"privileges":["CREATE","INSERT","SELECT","UPDATE"],"instance_id":'"${INSTANCE_ID}"',"for_all":false}' > /dev/null 2>&1
#  echo -e "\n✔ Пользователь $ID_USER обработан"
  done

  for ID_USER in "${ID_USERS[@]}"; do
curl "https://timeweb.cloud/api/v1/databases/${DB_ID}/admins/${ID_USER}" \
  -X 'PATCH' \
  -H 'content-type: application/json' \
  -H "authorization: Bearer ${TOKEN}" \
  --data-raw '{"privileges":["CREATE_DB","CREATE","INSERT","SELECT","UPDATE","DELETE","CREATE_VIEW","SHOW_VIEW","INDEX","ALTER","LOCK_TABLES","REFERENCES","TRIGGER","CREATE_ROUTINE","ALTER_ROUTINE","CREATE_TEMPORARY_TABLES","EVENT","DROP","CREATE_USER","PROCESS","SLOW_LOG"],"instance_id":'"${INSTANCE_ID}"',"for_all":false}'
#  echo -e "\n✔ Пользователь $ID_USER обработан"
echo "${INSTANCE_ID}"
done
  sleep 5
}


function off_prava () {
for ID_USER in "${ID_USERS[@]}"; do
curl "https://timeweb.cloud/api/v1/databases/${DB_ID}/admins/${ID_USER}" \
  -X 'PATCH' \
  -H 'content-type: application/json' \
  -H "authorization: Bearer ${TOKEN}" \
  --data-raw '{"privileges":[],"instance_id":'"${INSTANCE_ID}"',"for_all":false}'
  echo -e "\n✔ Пользователь $ID_USER обработан"
  echo "URL: https://timeweb.cloud/api/v1/databases/${DB_ID}/admins/${ID_USER}"

done

sleep 30
}

off_prava

