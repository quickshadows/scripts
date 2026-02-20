# create_dbas - Утилита для создания баз данных

Автономная утилита для создания баз данных через Timeweb Cloud API.

## Структура

```
create_dbas/
├── lib/                    # Библиотеки
│   ├── db/                # Работа с БД
│   │   ├── api_client.py  # Клиент API
│   │   ├── ip_manager.py  # Управление IP
│   │   └── database_factory.py
│   └── utils/             # Утилиты
│       ├── config_loader.py
│       └── logging.py
├── config/                 # Конфигурации
│   ├── db_config.yaml     # Базовая конфигурация
│   └── environments/      # Конфигурации окружений
│       ├── prod.yaml
│       ├── stage.yaml
│       └── dev.yaml
└── scripts/               # Скрипты
    └── create_all.py      # Основной скрипт
```

## Установка зависимостей

```bash
pip install requests pyyaml
```

## Настройка

1. Установите переменную окружения:
```bash
export TIMEWEB_CLOUD_TOKEN="your_token_here"
```

2. При необходимости переопределите другие параметры:
```bash
export NETWORK_ID="network-xxx"
export PROJECT_ID=123456
export ENV=prod
```

## Использование

### Интерактивный режим

```bash
cd create_dbas
./create_all.py --interactive
# или просто
./create_all.py
```

### Командная строка

```bash
# Создать все PostgreSQL базы для production
./create_all.py --env prod --db-type postgres

# Создать MySQL кластер для staging
./create_all.py --env stage --db-type mysql --cluster

# Создать все базы для production
./create_all.py --env prod --db-type all
```

## Поддерживаемые типы БД

- MySQL (mysql, mysql8_4)
- PostgreSQL (postgres14-18)
- Redis (redis7, redis8_1)
- MongoDB (mongodb7, mongodb8_0)
- ClickHouse (clickhouse, clickhouse24, clickhouse25)
- OpenSearch (opensearch2_19)
- Kafka (kafka)
- RabbitMQ (rabbitmq4_0)

## Конфигурация

### Базовая конфигурация (`config/db_config.yaml`)

Содержит:
- `default_config` - конфигурация по умолчанию (configurator)
- `database_types` - mapping типов БД и их preset_id (опционально)

### Конфигурации окружений (`config/environments/*.yaml`)

Содержат:
- `databases` - список БД для создания
- `api_base_url_v1`, `api_base_url_v2` - API endpoints
- `databases_url` - endpoint для создания БД (может отличаться для stage)
- `auto_backups` - настройки автоматических бэкапов

## Логика работы

1. **По умолчанию** используется `default_config` (configurator)
2. Если в конфигурации БД указан `preset_id` - используется он вместо configurator
3. API не принимает одновременно `preset_id` и `configuration`

## Безопасность

- Токен берется из переменной окружения `TIMEWEB_CLOUD_TOKEN`
- Никогда не храните токены в конфигурационных файлах
- Используйте `.env` файлы для локальной разработки
