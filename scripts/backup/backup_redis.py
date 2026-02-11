#!/usr/bin/env python3
"""
Бэкап Redis: копирование RDB-файла. Опционально выполнить BGSAVE и ждать сохранения.
Нужно знать путь к dump.rdb (из конфига Redis или --rdb-path).
Использование:
  python3 backup_redis.py --dest /backup/redis [--rdb-path /var/lib/redis/dump.rdb] [--bgsave] [--rotate-days N]
  С --bgsave: выполнить redis-cli BGSAVE и ждать завершения, затем копировать файл.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backup_common import dated_path, log, rotate_by_days, run


def main() -> int:
    parser = argparse.ArgumentParser(description="Бэкап Redis (копирование RDB)")
    parser.add_argument("--dest", required=True, help="Каталог для сохранения бэкапов")
    parser.add_argument("--rdb-path", default="/var/lib/redis/dump.rdb", help="Путь к dump.rdb на сервере Redis")
    parser.add_argument("--bgsave", action="store_true", help="Выполнить redis-cli BGSAVE и дождаться сохранения")
    parser.add_argument("--rotate-days", type=int, default=0, help="Удалить бэкапы старше N дней")
    parser.add_argument("--redis-cli", default="redis-cli", help="Путь к redis-cli")
    parser.add_argument("--host", default=os.environ.get("REDIS_HOST", "127.0.0.1"), help="Хост Redis")
    parser.add_argument("--port", type=int, default=int(os.environ.get("REDIS_PORT", "6379")), help="Порт Redis")
    args = parser.parse_args()

    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    rdb = Path(args.rdb_path)
    if not rdb.exists():
        log(f"Ошибка: RDB-файл не найден: {rdb}")
        return 1

    if args.bgsave:
        log("Выполняется BGSAVE...")
        code = run([args.redis_cli, "-h", args.host, "-p", str(args.port), "BGSAVE"], log_prefix="[redis-cli] ")
        if code != 0:
            return code
        log("Ожидание завершения сохранения (10 сек)...")
        time.sleep(10)

    out_path = dated_path(dest, "redis", ".rdb")
    log(f"Копирование {rdb} в {out_path}")
    try:
        import shutil
        shutil.copy2(rdb, out_path)
    except OSError as e:
        log(f"Ошибка копирования: {e}")
        return 1

    if args.rotate_days > 0:
        rotate_by_days(dest, "redis_", args.rotate_days)

    log("Готово.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
