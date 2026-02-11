# Бэкапы баз данных

Документация по скриптам бэкапа для всех поддерживаемых СУБД.

**Скрипты:** [../scripts/backup/](../scripts/backup/)

---

## Поддерживаемые СУБД

| СУБД | Скрипт | Инструмент | Формат вывода |
|------|--------|------------|---------------|
| PostgreSQL | `backup_postgres.py` | pg_dump / pg_dumpall | .dump (custom) или .sql (all) |
| MySQL / MariaDB | `backup_mysql.py` | mysqldump | .sql или .sql.gz |
| MongoDB | `backup_mongodb.py` | mongodump | каталог mongo_YYYY-MM-DD_HH-MM |
| Redis | `backup_redis.py` | копирование файла | .rdb |

## Ротация и проверка

| Скрипт | Назначение |
|--------|------------|
| `backup_rotate.py` | Удалить бэкапы старше N дней (`--days`) или оставить последние N файлов (`--keep`) по префиксу в каталоге. |
| `backup_verify.py` | Проверка целостности: PG — `pg_restore --list`, MySQL — `gunzip -t` для .gz, Mongo — наличие BSON, Redis — размер файла. |

Учётные данные задаются **переменными окружения** (см. README в `scripts/backup/`), не в коде.

---

## Примеры вызова

```bash
# PostgreSQL
python3 scripts/backup/backup_postgres.py --dest /backup/pg -d mydb --rotate-days 7

# MySQL (сжатие по умолчанию)
python3 scripts/backup/backup_mysql.py --dest /backup/mysql --all-databases --rotate-days 7

# MongoDB
python3 scripts/backup/backup_mongodb.py --dest /backup/mongo --gzip --rotate-days 7

# Redis (с предварительным BGSAVE)
python3 scripts/backup/backup_redis.py --dest /backup/redis --bgsave --rdb-path /var/lib/redis/dump.rdb

# Ротация: оставить 10 последних
python3 scripts/backup/backup_rotate.py --dir /backup/pg --prefix pg_mydb_ --keep 10

# Проверка
python3 scripts/backup/backup_verify.py -t pg -p /backup/pg/pg_mydb_2025-02-11_12-00.dump
```

---

## Требования

- Python 3.8+
- Утилиты: `pg_dump`/`pg_dumpall`/`pg_restore`, `mysqldump`, `mongodump`, `redis-cli`, `gzip`/`gunzip` (по мере использования скриптов).
