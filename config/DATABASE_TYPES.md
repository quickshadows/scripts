# Поддерживаемые типы баз данных

## Реляционные БД

### MySQL
- `mysql` - MySQL 8.0 (preset_id: 519)
- `mysql8_4` - MySQL 8.4 (preset_id: 519)

### PostgreSQL
- `postgres14` - PostgreSQL 14 (preset_id: 1175)
- `postgres15` - PostgreSQL 15 (preset_id: 1175)
- `postgres16` - PostgreSQL 16 (preset_id: 1175)
- `postgres17` - PostgreSQL 17 (preset_id: 1175)
- `postgres18` - PostgreSQL 18 (preset_id: 1175)

## NoSQL БД

### Redis
- `redis7` - Redis 7 (preset_id: 541)
- `redis8_1` - Redis 8.1 (preset_id: 541)

### MongoDB
- `mongodb7` - MongoDB 7 (preset_id: 515)
- `mongodb8_0` - MongoDB 8.0 (preset_id: 515)

## Аналитические БД

### ClickHouse
- `clickhouse` - ClickHouse (preset_id: 1229)
- `clickhouse24` - ClickHouse 24 (preset_id: 1229)
- `clickhouse25` - ClickHouse 25 (preset_id: 1229)

## Поисковые системы

### OpenSearch
- `opensearch2_19` - OpenSearch 2.19 (preset_id: 747)

## Очереди сообщений

### Kafka
- `kafka` - Apache Kafka (preset_id: 759)

### RabbitMQ
- `rabbitmq4_0` - RabbitMQ 4.0 (preset_id: 805)

## Особенности конфигурации

### Типы БД с поддержкой hash_type
Только MySQL типы поддерживают параметр `hash_type`:
- `mysql`
- `mysql8_4`

### Типы БД с поддержкой admin пароля
Следующие типы БД требуют настройки администратора:
- Все MySQL типы
- Все PostgreSQL типы
- MongoDB типы

### Типы БД без admin пароля
Следующие типы БД не требуют настройки администратора:
- Redis
- ClickHouse
- OpenSearch
- Kafka
- RabbitMQ

### Поддержка кластеров
Кластеры поддерживаются для:
- MySQL
- PostgreSQL
- MongoDB
- Redis

Остальные типы БД создаются только как одиночные инстансы.
