#!/usr/bin/env bash
# generate_cms_like_data.sh
# Генерирует CMS-like данные (users, posts, postmeta, comments, terms, term_relationships)
# в указанной MySQL базе до приблизительного размера target_gb.
#
# Usage:
#   ./generate_cms_like_data.sh HOST PORT USER PASS DB TARGET_GB [BATCH_ROWS]
#
# Example:
#   ./generate_cms_like_data.sh 127.0.0.1 3306 root 'Passw0rd' wp_test 8 1000
#
set -euo pipefail

#if [ "$#" -lt 6 ]; then
#  echo "Usage: $0 HOST PORT USER PASS DB TARGET_GB [BATCH_ROWS]"
#  exit 1
#fi

HOST="2.59.40.195"
PORT="3306"
USER="gen_user"
PASS="Passwd123"
DB="db1"
TARGET_GB="8"
BATCH_ROWS="${7:-1000}"   # сколько строк вставлять за один пакет в основных таблицах

# mysql client wrapper
MYSQL="mysql -h${HOST} -P${PORT} -u${USER} -p${PASS} --default-character-set=utf8mb4 --connect-timeout=10 ${DB} -sNe"

echo "=== Генерация CMS-like данных ==="
echo "Target size: ${TARGET_GB} GB, batch rows: ${BATCH_ROWS}"
echo "Подключение к ${HOST}:${PORT} базa ${DB} как ${USER}"

read -p "Продолжить? (type 'yes' to continue): " confirm
if [ "$confirm" != "yes" ]; then
  echo "Отменено."
  exit 1
fi

# расчёты
TARGET_BYTES=$(( TARGET_GB * 1024 * 1024 * 1024 ))
echo "Целевой объём (байт): $TARGET_BYTES"

# Создаём схему (упрощённая WP-like)
echo "Создаю таблицы (если не существуют)..."
$MYSQL <<'SQL'
CREATE TABLE IF NOT EXISTS wp_users (
  ID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_login VARCHAR(60),
  user_pass VARCHAR(255),
  user_email VARCHAR(100),
  user_registered DATETIME,
  display_name VARCHAR(100),
  INDEX(user_login),
  INDEX(user_email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS wp_posts (
  ID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  post_author BIGINT UNSIGNED,
  post_date DATETIME,
  post_title VARCHAR(255),
  post_content LONGTEXT,
  post_excerpt TEXT,
  post_status VARCHAR(20),
  post_type VARCHAR(20),
  INDEX(post_author),
  INDEX(post_status),
  INDEX(post_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS wp_postmeta (
  meta_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  post_id BIGINT UNSIGNED,
  meta_key VARCHAR(255),
  meta_value MEDIUMTEXT,
  INDEX(post_id),
  INDEX(meta_key(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS wp_comments (
  comment_ID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  comment_post_ID BIGINT UNSIGNED,
  comment_author VARCHAR(255),
  comment_author_email VARCHAR(100),
  comment_date DATETIME,
  comment_content TEXT,
  comment_approved VARCHAR(20),
  INDEX(comment_post_ID),
  INDEX(comment_approved)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS wp_terms (
  term_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200),
  slug VARCHAR(200),
  INDEX(slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS wp_term_relationships (
  object_id BIGINT UNSIGNED,
  term_taxonomy_id BIGINT UNSIGNED,
  PRIMARY KEY (object_id, term_taxonomy_id),
  INDEX(term_taxonomy_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS wp_options (
  option_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  option_name VARCHAR(191),
  option_value MEDIUMTEXT,
  autoload VARCHAR(20),
  INDEX(option_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
SQL

echo "Таблицы созданы."

# Вспомогательная функция: вставлять пакеты INSERT
bulk_insert_posts() {
  # args: table rows batch_size avg_content_len
  local rows="$1"; local batch="$2"; local avg_len="$3"

  local i=0
  while [ $i -lt $rows ]; do
    local end=$(( i + batch ))
    if [ $end -gt $rows ]; then end=$rows; fi

    # формируем пакет INSERT
    (
      printf "INSERT INTO wp_posts (post_author, post_date, post_title, post_content, post_excerpt, post_status, post_type) VALUES "
      local first=1
      for ((j=i; j<end; j++)); do
        # делаем псевдослучайный текст нужной длины
        content=$(head -c $avg_len /dev/urandom | tr -dc 'a-zA-Z0-9 ,.?!' | tr -s ' ' | sed "s/'/\\\'/g")
        title=$(head -c 60 /dev/urandom | tr -dc 'a-zA-Z0-9 ' | tr -s ' ' | sed "s/'/\\\'/g")
        date="2020-01-01"
        if [ $first -eq 0 ]; then printf ","; fi
        printf " (1, '%s', '%s', '%s', '%s', 'publish', 'post') " "$date" "$title" "$content" "$(echo "$content" | cut -c1-200)"
        first=0
      done
      printf ";\n"
    ) >> /tmp/_bulk_posts.sql

    # выполнить пакет
    $MYSQL < /tmp/_bulk_posts.sql
    rm -f /tmp/_bulk_posts.sql

    i=$end
    echo -n "."
  done
  echo
}

# функция для вставки метаданных и комментариев (bulk)
bulk_insert_postmeta() {
  local rows="$1"; local batch="$2"; local avg_len="$3"
  local i=0
  while [ $i -lt $rows ]; do
    local end=$(( i + batch ))
    if [ $end -gt $rows ]; then end=$rows; fi
    (
      printf "INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES "
      local first=1
      for ((j=i; j<end; j++)); do
        meta=$(head -c $avg_len /dev/urandom | tr -dc 'a-zA-Z0-9 ' | tr -s ' ' | sed "s/'/\\\'/g")
        mk="meta_key_$(($RANDOM % 100))"
        if [ $first -eq 0 ]; then printf ","; fi
        # распределяем post_id равномерно по имеющимся постам (ID примерно последовательный)
        pid=$(( (j % 1000000) + 1 ))
        printf " (%d, '%s', '%s') " "$pid" "$mk" "$meta"
        first=0
      done
      printf ";\n"
    ) >> /tmp/_bulk_meta.sql
    $MYSQL < /tmp/_bulk_meta.sql
    rm -f /tmp/_bulk_meta.sql
    i=$end
    echo -n "."
  done
  echo
}

bulk_insert_comments() {
  local rows="$1"; local batch="$2"; local avg_len="$3"
  local i=0
  while [ $i -lt $rows ]; do
    local end=$(( i + batch ))
    if [ $end -gt $rows ]; then end=$rows; fi
    (
      printf "INSERT INTO wp_comments (comment_post_ID, comment_author, comment_author_email, comment_date, comment_content, comment_approved) VALUES "
      local first=1
      for ((j=i; j<end; j++)); do
        author=$(head -c 30 /dev/urandom | tr -dc 'a-zA-Z' | tr -s ' ' | sed "s/'/\\\'/g")
        email="${author}@example.com"
        content=$(head -c $avg_len /dev/urandom | tr -dc 'a-zA-Z0-9 ,.?!' | tr -s ' ' | sed "s/'/\\\'/g")
        pid=$(( (j % 1000000) + 1 ))
        if [ $first -eq 0 ]; then printf ","; fi
        printf " (%d, '%s', '%s', '2020-01-01', '%s', '1') " "$pid" "$author" "$email" "$content"
        first=0
      done
      printf ";\n"
    ) >> /tmp/_bulk_comments.sql
    $MYSQL < /tmp/_bulk_comments.sql
    rm -f /tmp/_bulk_comments.sql
    i=$end
    echo -n "."
  done
  echo
}

# Оценим начальный размер БД (байты)
initial_size=$($MYSQL "SELECT IFNULL(SUM(data_length+index_length),0) FROM information_schema.tables WHERE table_schema='$DB';")
echo "Текущий размер БД (байт): $initial_size"

remaining=$(( TARGET_BYTES - initial_size ))
if [ $remaining -le 0 ]; then
  echo "БД уже больше или равна целевому объёму. Выходим."
  exit 0
fi
echo "Требуется сгенерировать приблизительно: $remaining байт"

# Стратегия генерации:
#  - Создадим N пользователей (не много)
#  - Сгенерируем много постов с большим post_content (LONGTEXT) — основной вклад в размер
#  - Добавим постмета и комментарии (много мелких строк)
#  - Проверяем текущий размер после каждой фазы и продолжаем, пока не достигнем target

# 1) Создадим 1000 пользователей
echo "Вставляем пользователей..."
$MYSQL <<'SQL'
INSERT INTO wp_users (user_login, user_pass, user_email, user_registered, display_name)
SELECT CONCAT('user', LPAD(t.n,6,'0')), 'pass', CONCAT('user',LPAD(t.n,6,'0'),'@example.com'), NOW(), CONCAT('User ', t.n)
FROM (
  SELECT @row := @row + 1 AS n FROM
  (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4) a,
  (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4) b,
  (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4) c,
  (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4) d,
  (SELECT @row := 0) r
  LIMIT 1000
) t;
SQL
echo "OK."

# loop: добавляем блоки постов пока не достигли размера
phase=0
while [ $remaining -gt 0 ]; do
  phase=$((phase+1))
  echo "=== Фаза $phase: remaining $remaining байт ==="

  # ориентируемся, что каждая запись поста даст в среднем ~avg_post_bytes байт
  # управляем avg_post_bytes чтобы не создавать гигантских строк
  if [ $remaining -gt $((1024*1024*1024)) ]; then
    avg_post_bytes=20000   # ~20 KB контента -> быстрее наращивает
    posts_to_create=$(( remaining / avg_post_bytes / 2 ))  # делаем сначала половину
    [ $posts_to_create -lt 100 ] && posts_to_create=100
  elif [ $remaining -gt $((500*1024*1024)) ]; then
    avg_post_bytes=10000   # 10 KB
    posts_to_create=$(( remaining / avg_post_bytes / 2 ))
    [ $posts_to_create -lt 100 ] && posts_to_create=100
  else
    avg_post_bytes=4000    # 4 KB
    posts_to_create=$(( remaining / avg_post_bytes ))
    [ $posts_to_create -lt 100 ] && posts_to_create=100
  fi

  # ограничим разумно
  if [ $posts_to_create -gt 200000 ]; then posts_to_create=200000; fi

  echo "Добавляем примерно $posts_to_create постов, средний размер контента $avg_post_bytes байт."

  # выполняем пакетную вставку в чанках BATCH_ROWS
  created=0
  while [ $created -lt $posts_to_create ]; do
    chunk=$BATCH_ROWS
    left=$((posts_to_create - created))
    if [ $left -lt $chunk ]; then chunk=$left; fi

    # формируем один bulk INSERT: используем here-doc для скорости
    {
      printf "INSERT INTO wp_posts (post_author, post_date, post_title, post_content, post_excerpt, post_status, post_type) VALUES "
      first=1
      for k in $(seq 1 $chunk); do
        # генерируем контент заданной длины без мультибайтовых проблем — повторяем шаблон
        snippet="Lorem ipsum dolor sit amet. "
        repeat=$(( avg_post_bytes / ${#snippet} ))
        if [ $repeat -lt 1 ]; then repeat=1; fi
        content=$(printf "%.0s$snippet" $(seq 1 $repeat))
        title="Post $(date +%s%N)$RANDOM"
        if [ $first -eq 0 ]; then printf ","; fi
        printf " (1, NOW(), '%s', '%s', '%s', 'publish', 'post') " "${title//\'/\\\'}" "${content//\'/\\\'}" "${content:0:200//\'/\\\'}"
        first=0
      done
      printf ";\n"
    } > /tmp/_bulk_posts.sql

    $MYSQL < /tmp/_bulk_posts.sql
    rm -f /tmp/_bulk_posts.sql

    created=$((created + chunk))
    echo -n "."
  done
  echo

  # после вставки пересчитаем размер
  cur_size=$($MYSQL "SELECT IFNULL(SUM(data_length+index_length),0) FROM information_schema.tables WHERE table_schema='${DB}';")
  remaining=$(( TARGET_BYTES - cur_size ))
  echo "Текущий размер: $cur_size, remaining: $remaining"

  # добавим postmeta и комментарии, чтобы повысить количество строк
  if [ $remaining -gt 0 ]; then
    meta_to_add=$(( posts_to_create * 3 ))   # 3 meta per post
    echo "Добавляем примерно $meta_to_add записей в postmeta"
    bulk_insert_postmeta "$meta_to_add" "$BATCH_ROWS" 200
    comm_to_add=$(( posts_to_create / 2 ))
    echo "Добавляем примерно $comm_to_add комментариев"
    bulk_insert_comments "$comm_to_add" "$BATCH_ROWS" 200
  fi

  # обновим размер
  cur_size=$($MYSQL "SELECT IFNULL(SUM(data_length+index_length),0) FROM information_schema.tables WHERE table_schema='${DB}';")
  remaining=$(( TARGET_BYTES - cur_size ))
  echo "После meta/comments: текущий размер: $cur_size, remaining: $remaining"

  # если зацикливаемся — снизим avg_post_bytes
  if [ $phase -gt 40 ]; then
    echo "Достигнут предел итераций, выходим."
    break
  fi
done

echo "Генерация завершена. Финальный размер БД (байт): $($MYSQL "SELECT IFNULL(SUM(data_length+index_length),0) FROM information_schema.tables WHERE table_schema='${DB}';")"

echo "Рекомендуется выполнить OPTIMIZE TABLE для больших таблиц если нужно."
echo "Ниже — пример команды для проверки:"
echo "mysql -h${HOST} -P${PORT} -u${USER} -p'*****' -e \"SELECT table_name, ROUND((data_length+index_length)/1024/1024,2) AS mb FROM information_schema.tables WHERE table_schema='${DB}' ORDER BY (data_length+index_length) DESC LIMIT 20;\""

exit 0
