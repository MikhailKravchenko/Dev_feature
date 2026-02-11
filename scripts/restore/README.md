# Восстановление из бэкапов

Сценарии восстановления для PostgreSQL, MySQL/MariaDB, MongoDB и Redis.

| Скрипт | Описание |
|--------|----------|
| `restore_postgres.py` | PostgreSQL: pg_restore из .dump (custom) или каталога; опционально --create-db, --clean |
| `restore_mysql.py` | MySQL/MariaDB: восстановление из .sql или .sql.gz (через stdin) |
| `restore_mongodb.py` | MongoDB: mongorestore из каталога дампа, опции --drop, --gzip |
| `restore_redis.sh` | Redis: подмена RDB-файла, опционально перезапуск сервиса (--restart) |

## Переменные окружения

- **PostgreSQL:** `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`
- **MySQL:** `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PWD` (или `MYSQL_PASSWORD`)
- **MongoDB:** `MONGODB_URI` или `MONGODB_HOST`, `MONGODB_PORT`
- **Redis (скрипт):** `RDB_PATH` (целевой путь к dump.rdb), `REDIS_SERVICE` (имя systemd-юнита)

## Примеры

```bash
# PostgreSQL (бэкап в формате custom)
export PGPASSWORD=...
python3 restore_postgres.py --backup /backup/pg/pg_mydb_2025-02-11.dump --database mydb --create-db
python3 restore_postgres.py --backup /backup/pg/pg_mydb_2025-02-11.dump -d mydb --clean

# MySQL/MariaDB
export MYSQL_PWD=...
python3 restore_mysql.py --backup /backup/mysql/mysql_all_2025-02-11.sql.gz
python3 restore_mysql.py --backup /backup/mysql/mysql_mydb_2025-02-11.sql -d mydb

# MongoDB
export MONGODB_URI="mongodb://localhost:27017"
python3 restore_mongodb.py --backup /backup/mongo/mongo_2025-02-11_12-00 --drop
python3 restore_mongodb.py --backup /backup/mongo/mongo_2025-02-11_12-00 --gzip

# Redis (остановка, подмена RDB, запуск — может потребоваться sudo)
chmod +x restore_redis.sh
./restore_redis.sh --backup /backup/redis/redis_2025-02-11.rdb --rdb-path /var/lib/redis/dump.rdb --restart
```

**Важно:** перед восстановлением убедитесь, что целевой сервер/БД доступен и при необходимости остановите приложение или переведите его в режим обслуживания. Redis: при --restart данные в памяти до перезапуска будут потеряны (восстанавливается состояние из RDB).

**Документация:** [../../docs/restore.md](../../docs/restore.md)
