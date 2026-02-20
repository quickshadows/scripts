# Scripts - Скрипты для управления базами данных и S3

Коллекция скриптов для автоматизации работы с базами данных Timeweb Cloud и S3 хранилищем.

## 📁 Структура проекта

```
scripts/
├── config/                    # Конфигурационные файлы
│   ├── db_config.yaml        # Базовая конфигурация БД
│   ├── s3_config.yaml        # Конфигурация S3
│   ├── environments/         # Конфигурации по окружениям
│   │   ├── prod.yaml
│   │   ├── stage.yaml
│   │   └── dev.yaml
│   └── DATABASE_TYPES.md     # Документация по типам БД
│
├── lib/                       # Переиспользуемые библиотеки
│   ├── db/                   # Библиотеки для работы с БД
│   │   ├── api_client.py
│   │   ├── ip_manager.py
│   │   └── database_factory.py
│   ├── s3/                   # Библиотеки для работы с S3
│   │   ├── client.py
│   │   └── multipart.py
│   └── utils/                # Утилиты
│       ├── config_loader.py
│       └── logging.py
│
├── dbas/                      # Скрипты для работы с БД
│   ├── create/               # Создание БД
│   │   └── create_all.py    # Универсальный скрипт создания
│   ├── manage/               # Управление БД
│   │   ├── mysql/
│   │   └── postgres/
│   ├── testing/              # Тестирование
│   │   └── performance/
│   │       ├── sysbench_mysql.sh
│   │       └── sysbench_pg.sh
│   └── data/                 # Генерация данных
│
├── s3/                        # Скрипты для работы с S3
│   ├── upload/               # Загрузка файлов
│   │   └── multipart_upload.py
│   ├── operations/           # Операции с объектами
│   │   ├── copy.py
│   │   └── delete.py
│   └── monitoring/           # Мониторинг
│
└── archive/                   # Архивированные скрипты
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install boto3 pyyaml requests
```

### 2. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и заполните значениями:

```bash
cp .env.example .env
```

Отредактируйте `.env`:
```bash
TIMEWEB_CLOUD_TOKEN=your_token_here
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
ENV=dev
```

### 3. Использование

#### Создание баз данных

```bash
# Создать все PostgreSQL базы для production
python dbas/create/create_all.py --env prod --db-type postgres

# Создать MySQL кластер для staging
python dbas/create/create_all.py --env stage --db-type mysql --cluster

# Создать все базы для production
python dbas/create/create_all.py --env prod --db-type all

# Интерактивный режим
python dbas/create/create_all.py --interactive
```

#### Работа с S3

```bash
# Копирование объекта
python s3/operations/copy.py --env prod --source-key config.yaml --dest-key config.yaml

# Удаление объекта
python s3/operations/delete.py --bucket my-bucket --key file.txt

# Multipart загрузка большого файла
python s3/upload/multipart_upload.py --file large_file.bin --bucket my-bucket --key large_file.bin
```

#### Тестирование производительности

```bash
# Тест MySQL
export MYSQL_HOST=localhost
export MYSQL_PASSWORD=password
./dbas/testing/performance/sysbench_mysql.sh

# Тест PostgreSQL
export PGSQL_HOST=localhost
export PGSQL_PASSWORD=password
./dbas/testing/performance/sysbench_pg.sh
```

## 📊 Поддерживаемые типы баз данных

- **MySQL**: mysql, mysql8_4
- **PostgreSQL**: postgres14, postgres15, postgres16, postgres17, postgres18
- **Redis**: redis7, redis8_1
- **MongoDB**: mongodb7, mongodb8_0
- **ClickHouse**: clickhouse, clickhouse24, clickhouse25
- **OpenSearch**: opensearch2_19
- **Kafka**: kafka
- **RabbitMQ**: rabbitmq4_0

Подробнее см. [config/DATABASE_TYPES.md](config/DATABASE_TYPES.md)

## ⚙️ Конфигурация

### Конфигурация БД

Основная конфигурация находится в `config/db_config.yaml`. Конфигурации для разных окружений в `config/environments/`.

### Конфигурация S3

Конфигурация S3 находится в `config/s3_config.yaml`.

## 🔧 Разработка

### Добавление нового типа БД

1. Добавьте тип в `config/db_config.yaml`:
```yaml
database_types:
  new_db_type:
    preset_id: 1234
```

2. Добавьте БД в конфигурации окружений (`config/environments/*.yaml`):
```yaml
databases:
  new_db:
    - name: "New DB api prod"
      type: "new_db_type"
      preset_id: 1234
```

3. При необходимости обновите `lib/db/api_client.py` для поддержки специфичных параметров типа БД.

### Добавление нового скрипта

1. Разместите скрипт в соответствующей директории по функциональности
2. Используйте библиотеки из `lib/` для переиспользования кода
3. Используйте `lib/utils/config_loader.py` для загрузки конфигураций
4. Добавьте документацию в README

## 📝 Примеры использования

### Создание всех баз данных для staging

```bash
python dbas/create/create_all.py --env stage --db-type all
```

### Создание кластера PostgreSQL для production

```bash
python dbas/create/create_all.py --env prod --db-type postgres --cluster
```

### Копирование файла между бакетами

```bash
python s3/operations/copy.py \
  --env prod \
  --source-key config.yaml \
  --dest-key backup/config.yaml
```

## 🔒 Безопасность

- **Никогда не коммитьте секреты** в репозиторий
- Используйте `.env` файлы для хранения секретов (добавлен в `.gitignore`)
- Используйте переменные окружения для продакшена
- Регулярно ротируйте токены и ключи доступа

## 📚 Дополнительная документация

- [Анализ структуры проекта](АНАЛИЗ_СТРУКТУРЫ.md)
- [Сравнение структур](STRUCTURE_COMPARISON.md)
- [Детальный анализ](STRUCTURE_ANALYSIS.md)
- [Типы баз данных](config/DATABASE_TYPES.md)

## 🤝 Вклад

При внесении изменений:
1. Создайте ветку для изменений
2. Следуйте существующей структуре проекта
3. Используйте библиотеки из `lib/` вместо дублирования кода
4. Обновляйте документацию
5. Тестируйте изменения перед коммитом

## 📄 Лицензия

Внутренний проект.
