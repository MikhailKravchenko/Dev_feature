# Бэкапы баз данных

Скрипты бэкапа для PostgreSQL, MySQL/MariaDB, MongoDB, Redis. Общий модуль: ротация, пути с датой.

| Скрипт | Описание |
|--------|----------|
| `backup_common.py` | Общие утилиты: dated_path, run, log, rotate_by_days, rotate_keep_n |
| `backup_postgres.py` | PostgreSQL: pg_dump (одна БД) или pg_dumpall, формат custom, ротация |
| `backup_mysql.py` | MySQL/MariaDB: mysqldump, сжатие gzip, ротация |
| `backup_mongodb.py` | MongoDB: mongodump в каталог с датой, опция --gzip, ротация каталогов |
| `backup_redis.py` | Redis: копирование RDB-файла, опционально BGSAVE перед копированием |
| `backup_rotate.py` | Ротация: удалить старше N дней (--days) или оставить последние N (--keep) |
| `backup_verify.py` | Проверка целостности: pg_restore --list, gunzip -t, наличие файлов |

## Переменные окружения (учётные данные не в коде)

- **PostgreSQL:** `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`
- **MySQL:** `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PWD` (или `MYSQL_PASSWORD`), `MYSQL_DATABASE`
- **MongoDB:** `MONGODB_URI`
- **Redis:** `REDIS_HOST`, `REDIS_PORT` (путь к RDB задаётся `--rdb-path`)

## Примеры

```bash
# PostgreSQL: одна БД, ротация 7 дней
export PGPASSWORD=secret
python3 backup_postgres.py --dest /backup/pg --database mydb --rotate-days 7

# PostgreSQL: все БД
python3 backup_postgres.py --dest /backup/pg --all --rotate-days 7

# MySQL: все БД, сжатие, ротация
export MYSQL_PWD=secret
python3 backup_mysql.py --dest /backup/mysql --all-databases --rotate-days 7

# MongoDB
export MONGODB_URI="mongodb://localhost:27017"
python3 backup_mongodb.py --dest /backup/mongo --gzip --rotate-days 7

# Redis: скопировать RDB (путь по умолчанию /var/lib/redis/dump.rdb)
python3 backup_redis.py --dest /backup/redis --rdb-path /var/lib/redis/dump.rdb --rotate-days 7

# Redis: перед копированием выполнить BGSAVE
python3 backup_redis.py --dest /backup/redis --bgsave --rotate-days 7

# Ротация вручную: оставить последние 10 файлов
python3 backup_rotate.py --dir /backup/pg --prefix pg_mydb_ --keep 10

# Ротация: удалить старше 14 дней
python3 backup_rotate.py --dir /backup/pg --prefix pg_mydb_ --days 14

# Проверка целостности
python3 backup_verify.py --type pg --path /backup/pg/pg_mydb_2025-02-11_12-00.dump
python3 backup_verify.py --type mysql --path /backup/mysql/mysql_all_2025-02-11_12-00.sql.gz
python3 backup_verify.py --type redis --path /backup/redis/redis_2025-02-11_12-00.rdb
```

**Документация:** [../../docs/backups.md](../../docs/backups.md)
