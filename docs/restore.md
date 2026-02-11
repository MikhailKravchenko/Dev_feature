# Восстановление из бэкапов

Сценарии восстановления для каждой СУБД. Учётные данные — через переменные окружения.

**Скрипты:** [../scripts/restore/](../scripts/restore/)

---

## СУБД

| СУБД | Скрипт | Действия |
|------|--------|----------|
| PostgreSQL | `restore_postgres.py` | pg_restore из .dump (custom) или каталога (directory). Опции: --create-db (createdb), --clean (удалить объекты перед восстановлением), --no-owner. |
| MySQL / MariaDB | `restore_mysql.py` | Восстановление из .sql или .sql.gz: поток передаётся в mysql через stdin. Опционально --database для одной БД. |
| MongoDB | `restore_mongodb.py` | mongorestore из каталога дампа (результат mongodump). Опции: --drop (удалить коллекции перед восстановлением), --gzip. |
| Redis | `restore_redis.sh` | Подмена RDB: копирование файла бэкапа в целевой путь (по умолчанию /var/lib/redis/dump.rdb), при необходимости — systemctl stop/start (--restart). Текущий dump.rdb сохраняется с суффиксом .before_restore.* |

---

## Предупреждения

1. **Перед восстановлением** убедитесь, что используете правильный файл/каталог бэкапа и целевую БД/сервер.
2. **PostgreSQL:** --clean удаляет объекты в целевой БД перед восстановлением; при необходимости сначала создайте БД (--create-db).
3. **MySQL:** при дампе одной БД укажите --database; при --all-databases не указывайте --database.
4. **MongoDB:** --drop удаляет существующие коллекции с теми же именами перед восстановлением.
5. **Redis:** при --restart сервис останавливается, подменяется RDB, затем запускается; для перезапуска могут потребоваться права (sudo). Имя сервиса задаётся переменной REDIS_SERVICE (по умолчанию redis-server).

---

## Примеры вызова

```bash
# PostgreSQL
python3 scripts/restore/restore_postgres.py -b /backup/pg/pg_mydb_2025-02-11.dump -d mydb --create-db

# MySQL
python3 scripts/restore/restore_mysql.py -b /backup/mysql/mysql_all_2025-02-11.sql.gz

# MongoDB
python3 scripts/restore/restore_mongodb.py -b /backup/mongo/mongo_2025-02-11_12-00 --drop

# Redis
./scripts/restore/restore_redis.sh --backup /backup/redis/redis_2025-02-11.rdb --restart
```

Требования: Python 3.8+ для Python-скриптов; для Redis — bash, systemctl, права на запись в каталог данных и перезапуск сервиса.
