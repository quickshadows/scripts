import psycopg2

databases = [
    "postgresql://gen_user:Pass@81.200.145.49:5432/default_db",
    "postgresql://gen_user:Pass@176.57.220.211:5432/default_db",
]

for db_url in databases:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Получение списка всех таблиц
    cur.execute("ALTER USER psql_create_user TO psql_alter_user;")

    # Завершение транзакции и закрытие соединения
    conn.commit()
    cur.close()
    conn.close()
