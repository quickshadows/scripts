# Сводка: Утилита create_dbas

## Что включено

Утилита `create_dbas` - это автономный инструмент для создания баз данных через Timeweb Cloud API.

### Структура

```
create_dbas/
├── lib/                    # Библиотеки
│   ├── db/                # Работа с БД
│   │   ├── api_client.py  # Клиент Timeweb Cloud API
│   │   ├── ip_manager.py  # Управление IP-адресами
│   │   └── database_factory.py  # Фабрика создания БД
│   └── utils/             # Утилиты
│       ├── config_loader.py  # Загрузка конфигураций
│       └── logging.py        # Настройка логирования
├── config/                 # Конфигурации
│   ├── db_config.yaml     # Базовая конфигурация БД
│   └── environments/      # Конфигурации окружений
│       ├── prod.yaml
│       ├── stage.yaml
│       └── dev.yaml
├── create_all.py          # Основной скрипт создания БД
├── scripts/               # (опционально) совместимые врапперы
│   └── create_all.py
├── README.md              # Документация
└── .env.example          # Пример переменных окружения
```

## Что удалено из основной структуры

После вынесения утилиты из основной структуры удалены:

- `lib/db/` - перенесено в `create_dbas/lib/db/`
- `dbas/create/` - перенесено в `create_dbas/scripts/`
- `config/db_config.yaml` - перенесено в `create_dbas/config/`
- `config/environments/` - перенесено в `create_dbas/config/environments/`

## Что осталось в основной структуре

- `lib/s3/` - используется S3 скриптами
- `lib/utils/` - используется S3 скриптами
- `config/s3_config.yaml` - используется S3 скриптами
- `s3/` - скрипты для работы с S3
- `dbas/testing/` - тесты производительности
- `dbas/manage/` - управление БД
- `dbas/data/` - генерация данных

## Использование

```bash
cd create_dbas
./create_all.py --env prod --db-type postgres
```

Подробнее см. `create_dbas/README.md`
