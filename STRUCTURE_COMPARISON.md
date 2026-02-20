# Сравнение текущей и предлагаемой структуры

## Текущая структура (проблемы)

```
scripts/
├── archive/                    # ❌ Неорганизованный архив
├── bash/                      # ❌ Неясное назначение
│   └── multipart.sh
├── dbas/
│   ├── mysql/
│   │   ├── bash/
│   │   │   ├── test_speed_mysql.sh
│   │   │   ├── test_privileges.sh
│   │   │   ├── test.sh
│   │   │   └── create_prod_base.sh
│   │   └── py/
│   │       └── generate_mysql.py
│   ├── postgres/
│   │   ├── bash/
│   │   │   ├── test_speed_mysql.sh      ⚠️ MySQL тест в PG директории!
│   │   │   ├── test_speed_mysql_create.sh
│   │   │   ├── test_speed_mysql_del.sh
│   │   │   └── check_privileges.sh
│   │   └── py/
│   │       ├── create_user.py
│   │       ├── create_user_alter.py
│   │       ├── create_user_remove.py
│   │       ├── drop_table_pg.py
│   │       ├── gen_big_size.py
│   │       ├── load_test_prod.py
│   │       ├── pg_genegate.py
│   │       ├── show_table_pg.py
│   │       ├── synth_prod_db.py
│   │       └── test_time_create.py
│   ├── py/                    # ❌ Дублирование с mysql/py и postgres/py
│   │   ├── create_all.py
│   │   ├── create_mysql_prod.py
│   │   └── create_pg_prod.py
│   ├── speed/                 # ❌ Отдельная директория для тестов
│   │   ├── test_speed_mysql.sh
│   │   ├── test_speed_mysql_del.sh
│   │   ├── test_speed_pg.sh
│   │   └── test_speed_pg_del.sh
│   └── create_db_*.sh         # ❌ 10+ файлов с дублированием
│       ├── create_db_all_stage.sh
│       ├── create_db_mysql_cluster_prod.sh
│       ├── create_db_mysql_cluster_stage.sh
│       ├── create_db_mysql_prod.sh
│       ├── create_db_mysql_stage.sh
│       ├── create_db_pg_cluster_prod.sh
│       ├── create_db_pg_cluster_stage.sh
│       ├── create_db_pg_prod.sh
│       └── create_db_pg_stage.sh
└── s3/
    ├── bash/
    │   └── aws-api-check_v2.sh
    ├── go/
    │   ├── multipart_mas.go
    │   ├── multipart_mas_copy.go
    │   └── s3_upload_file_mas.go
    └── python/                # ❌ Непоследовательное именование
        ├── copy_file_dev.py
        ├── copy_file_prod.py
        ├── delete_multipart.py
        ├── s3_multipart.py
        ├── s3_multpart_mas.py
        └── s3_upload_file_mas.py
```

## Предлагаемая структура (решения)

```
scripts/
├── README.md                  # ✅ Подробная документация
├── .env.example              # ✅ Пример конфигурации
├── config/                   # ✅ Централизованные конфигурации
│   ├── db_config.yaml
│   ├── s3_config.yaml
│   └── environments/
│       ├── prod.yaml
│       ├── stage.yaml
│       └── dev.yaml
│
├── lib/                      # ✅ Переиспользуемый код
│   ├── db/
│   │   ├── __init__.py
│   │   ├── api_client.py     # Единый клиент API
│   │   ├── ip_manager.py     # Управление IP
│   │   └── database_factory.py
│   ├── s3/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   └── multipart.py
│   └── utils/
│       ├── __init__.py
│       ├── logging.py
│       └── config_loader.py
│
├── dbas/
│   ├── create/               # ✅ Единая точка создания БД
│   │   ├── create_all.py     # Универсальный скрипт
│   │   └── create_cluster.py
│   ├── manage/               # ✅ Управление БД
│   │   ├── mysql/
│   │   │   ├── users.py
│   │   │   └── privileges.sh
│   │   └── postgres/
│   │       ├── users.py
│   │       ├── tables.py
│   │       └── privileges.sh
│   ├── testing/              # ✅ Все тесты в одном месте
│   │   ├── performance/
│   │   │   ├── sysbench_mysql.sh
│   │   │   ├── sysbench_pg.sh
│   │   │   └── run_tests.py
│   │   └── load/
│   │       └── load_test.py
│   └── data/                 # ✅ Генерация данных
│       ├── generate_mysql.py
│       └── generate_pg.py
│
├── s3/
│   ├── upload/               # ✅ Логическая группировка
│   │   ├── simple_upload.py
│   │   ├── multipart_upload.py
│   │   └── batch_upload.py
│   ├── operations/           # ✅ Операции с объектами
│   │   ├── copy.py           # Единый скрипт с параметрами
│   │   ├── delete.py
│   │   └── list.py
│   └── monitoring/
│       └── api_check.sh
│
├── scripts/                  # ✅ Вспомогательные скрипты
│   └── multipart.sh
│
├── tests/                    # ✅ Тесты
│   ├── unit/
│   └── integration/
│
└── archive/                  # ✅ Старые файлы
```

## Ключевые улучшения

### 1. Устранение дублирования
- **Было:** 10+ файлов `create_db_*.sh`
- **Стало:** 1 файл `create_all.py` с параметрами

### 2. Правильная организация тестов
- **Было:** `test_speed_mysql.sh` в `postgres/bash/`
- **Стало:** `sysbench_mysql.sh` в `testing/performance/`

### 3. Централизация конфигураций
- **Было:** Хардкод в каждом файле
- **Стало:** Конфигурационные файлы + переменные окружения

### 4. Переиспользуемый код
- **Было:** Дублирование логики
- **Стало:** Библиотеки в `lib/`

### 5. Логическая группировка
- **Было:** Смешанная структура (по языку и по типу)
- **Стало:** По функциональности (create/manage/testing)

## Примеры использования новой структуры

### Создание БД
```bash
# Вместо множества файлов create_db_*.sh
python dbas/create/create_all.py --env prod --db-type mysql --cluster
python dbas/create/create_all.py --env stage --db-type postgres
```

### Тестирование производительности
```bash
# Вместо поиска файлов в разных директориях
python dbas/testing/performance/run_tests.py --db-type mysql --env prod
python dbas/testing/performance/run_tests.py --db-type postgres --env stage
```

### Работа с S3
```bash
# Вместо copy_file_prod.py и copy_file_dev.py
python s3/operations/copy.py --env prod --source bucket1 --dest bucket2
python s3/operations/copy.py --env dev --source bucket1 --dest bucket2
```
