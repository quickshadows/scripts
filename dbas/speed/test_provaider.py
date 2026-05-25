import subprocess
import csv
import shlex

os.environ['PGPASSWORD'] = "n@!fOXG|P*lQ9"


# ==================== Конфигурация баз ====================
# Список баз для теста
DBS = [
    {
        "provider": "timeweb_pg",
        "db_type": "postgres",
        "host": "185.211.170.131",
        "port": 5432,
        "user": "gen_user",
        "db_name": "default_db"
    },
    {
        "provider": "timeweb_mysql",
        "db_type": "mysql",
        "host": "37.77.106.215",
        "port": 3306,
        "user": "gen_user",
        "db_name": "default_db",
        "password": "Passwd123"
    }
]

# Кол-во клиентов/потоков
CLIENTS = 10
THREADS = 2
TIME = 60  # секунд

CSV_FILE = "db_perf_results.csv"

# ==================== Функции ====================
def run_pgbench(db):
    try:
        # Инициализация базы
        init_cmd = f"pgbench -i -s 10 -h {db['host']} -p {db['port']} -U {db['user']} {db['db_name']}"
        subprocess.run(shlex.split(init_cmd), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Запуск теста
        run_cmd = f"pgbench -c {CLIENTS} -j {THREADS} -T {TIME} -h {db['host']} -p {db['port']} -U {db['user']} {db['db_name']}"
        proc = subprocess.run(shlex.split(run_cmd), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Парсим вывод pgbench
        tps = None
        latency = None
        for line in proc.stdout.splitlines():
            if "including connections establishing" in line:
                tps = float(line.split('=')[1].split()[0])
            if "latency average" in line:
                latency = float(line.split('=')[1].split()[0])
        return tps, latency, ""
    except Exception as e:
        return None, None, str(e)

def run_sysbench(db):
    try:
        # Инициализация
        init_cmd = f"sysbench /usr/share/sysbench/oltp_read_write.lua --db-driver=mysql --mysql-host={db['host']} --mysql-port={db['port']} --mysql-user={db['user']} --mysql-password={db['password']} --mysql-db={db['db_name']} --tables=1 --table-size=100000 prepare"
        subprocess.run(shlex.split(init_cmd), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Запуск
        run_cmd = f"sysbench /usr/share/sysbench/oltp_read_write.lua --db-driver=mysql --mysql-host={db['host']} --mysql-port={db['port']} --mysql-user={db['user']} --mysql-password={db['password']} --mysql-db={db['db_name']} --tables=1 --table-size=100000 --threads={CLIENTS} --time={TIME} run"
        proc = subprocess.run(shlex.split(run_cmd), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Парсим вывод sysbench
        tps = None
        latency = None
        for line in proc.stdout.splitlines():
            if "transactions:" in line and "(" in line:
                parts = line.split('(')[1].split()
                tps = float(parts[0])
            if "avg:" in line:
                latency = float(line.split()[-1])
        # Очистка после теста
        cleanup_cmd = f"sysbench /usr/share/sysbench/oltp_read_write.lua --db-driver=mysql --mysql-host={db['host']} --mysql-port={db['port']} --mysql-user={db['user']} --mysql-password={db['password']} --mysql-db={db['db_name']} --tables=1 --table-size=100000 cleanup"
        subprocess.run(shlex.split(cleanup_cmd), check=True)
        return tps, latency, ""
    except Exception as e:
        return None, None, str(e)

# ==================== Основной цикл ====================
with open(CSV_FILE, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['provider','db_type','host','port','user','db_name','tps','latency_ms','error'])

    for db in DBS:
        print(f"Тестируем {db['provider']} ({db['db_type']}) ...")
        if db['db_type'] == "postgres":
            tps, latency, error = run_pgbench(db)
        elif db['db_type'] == "mysql":
            tps, latency, error = run_sysbench(db)
        else:
            tps, latency, error = None, None, "Unknown DB type"

        writer.writerow([
            db['provider'], db['db_type'], db['host'], db['port'], db['user'], db['db_name'],
            tps, latency, error
        ])
        print(f"Результат: TPS={tps}, Latency={latency} ms, Error={error}")

print(f"\nВсе результаты записаны в {CSV_FILE}")