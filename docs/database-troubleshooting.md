# Troubleshooting баз данных

На сервере быстро понять, **какие СУБД запущены** и **в каком они состоянии**: версия, соединения, память, репликация. Параметры, выходящие за допустимые рамки, подсвечиваются как **[WARN]**.

**Скрипты:** [../scripts/database/](../scripts/database/)

---

## Что делают скрипты

| Скрипт | Назначение |
|--------|------------|
| `detect_databases.py` | Проверка портов 5432, 3306, 27017, 6379; опционально проверка systemd (postgresql, mysql, mongod, redis). |
| `troubleshoot_all.py` | Определяет запущенные СУБД и для каждой запускает соответствующий troubleshoot_*. Вывод с подсветкой. |
| `troubleshoot_postgres.py` | Версия, соединения (текущие / max), shared_buffers, work_mem, роль (primary/replica), лаг реплики, долгие запросы (>60 сек), ожидающие блокировку, размер БД. |
| `troubleshoot_mysql.py` | Версия, соединения, InnoDB buffer pool и его использование, роль (master/slave), Seconds_Behind_Master, медленные запросы, открытые таблицы / table_open_cache. |
| `troubleshoot_mongodb.py` | Версия, соединения (current/available), память (resident, virtual), кэш WiredTiger, replica set и роль, очередь операций (globalLock). |
| `troubleshoot_redis.py` | Версия, клиенты (connected / maxclients), память (used_memory, maxmemory), персистентность (RDB, AOF), роль (master/slave), master_link_status, лаг. |

## Пороги (когда выводится [WARN])

- **Соединения:** использование лимита соединений > 80%.
- **PostgreSQL:** лаг реплики > 60 сек; наличие долгих запросов (>60 сек) или ожидающих блокировку.
- **MySQL:** использование buffer pool > 90%; table_open_cache > 80%; Seconds_Behind_Master > 60 сек; накопленные медленные запросы.
- **MongoDB:** использование соединений > 80%; кэш WiredTiger > 90%; очередь операций > 10.
- **Redis:** использование лимита клиентов > 80%; использование maxmemory > 90%; master_link_status не up; master_last_io_seconds_ago > 10.

## Переменные окружения

Учётные данные и хост/порт задаются через переменные окружения (не в коде):

- **PostgreSQL:** `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`
- **MySQL:** `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PWD` (или `MYSQL_PASSWORD`)
- **MongoDB:** `MONGODB_URI` или `MONGODB_HOST`, `MONGODB_PORT`
- **Redis:** `REDIS_HOST`, `REDIS_PORT`

## Примеры

```bash
# Попали на сервер — смотрим, что запущено
python3 scripts/database/detect_databases.py
python3 scripts/database/detect_databases.py --verbose

# Полный отчёт по всем обнаруженным СУБД (с подсветкой)
python3 scripts/database/troubleshoot_all.py

# Только одна СУБД (нужны переменные окружения для доступа)
export PGPASSWORD=...
python3 scripts/database/troubleshoot_all.py --only pg

export MYSQL_PWD=...
python3 scripts/database/troubleshoot_all.py --only mysql
```

В TTY используется цвет (зелёный [OK], красный [WARN]); при перенаправлении вывода — только префиксы. Отключить цвет: `NO_COLOR=1`.

## Требования

- Python 3.8+
- Клиенты: `psql` (PostgreSQL), `mysql` (MySQL/MariaDB), `mongosh` или `mongo` (MongoDB), `redis-cli` (Redis). Для определения по портам — только сокеты (стандартная библиотека).
