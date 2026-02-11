# Troubleshooting баз данных

На сервере быстро определить, **какие СУБД запущены**, и вывести **состояние и параметры** с подсветкой **[WARN]** при выходе за допустимые рамки.

| Скрипт | Описание |
|--------|----------|
| `detect_databases.py` | Определение запущенных СУБД по портам (5432, 3306, 27017, 6379), опционально systemd |
| `troubleshoot_all.py` | Единая точка входа: определяет БД и для каждой выводит состояние и параметры |
| `troubleshoot_postgres.py` | PostgreSQL: версия, соединения, память, репликация, долгие запросы, блокировки |
| `troubleshoot_mysql.py` | MySQL/MariaDB: соединения, InnoDB buffer pool, репликация, медленные запросы |
| `troubleshoot_mongodb.py` | MongoDB: соединения, память, WiredTiger cache, replica set, очередь операций |
| `troubleshoot_redis.py` | Redis: клиенты, память (used/maxmemory), персистентность, репликация |

## Пороги (подсветка [WARN])

- **Соединения:** использование лимита > 80% → предупреждение  
- **PostgreSQL:** лаг реплики > 60 сек, долгие запросы > 60 сек, ожидающие блокировку  
- **MySQL:** buffer pool > 90%, table_open_cache > 80%, Seconds_Behind_Master > 60, медленные запросы  
- **MongoDB:** соединения > 80%, кэш WiredTiger > 90%, очередь операций > 10  
- **Redis:** клиенты > 80% maxclients, использование maxmemory > 90%, master_link_status не up  

## Переменные окружения

- **PostgreSQL:** `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`  
- **MySQL:** `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PWD` (или `MYSQL_PASSWORD`)  
- **MongoDB:** `MONGODB_URI` или `MONGODB_HOST`, `MONGODB_PORT`  
- **Redis:** `REDIS_HOST`, `REDIS_PORT`  

## Примеры

```bash
# Определить, какие БД запущены
python3 detect_databases.py
python3 detect_databases.py --verbose

# Полный отчёт по всем обнаруженным СУБД (с подсветкой)
python3 troubleshoot_all.py

# Только PostgreSQL
python3 troubleshoot_all.py --only pg
export PGPASSWORD=... && python3 troubleshoot_postgres.py

# Только MySQL
export MYSQL_PWD=...
python3 troubleshoot_all.py --only mysql

# Только MongoDB / Redis
python3 troubleshoot_all.py --only mongo
python3 troubleshoot_all.py --only redis
```

Подсветка: в TTY вывод с цветом (зелёный [OK], красный [WARN]); при перенаправлении вывода — префиксы `[OK]` / `[WARN]`. Отключить цвет: `NO_COLOR=1`.
