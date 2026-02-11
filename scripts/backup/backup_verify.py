#!/usr/bin/env python3
"""
Проверка целостности бэкапов.
  PostgreSQL: pg_restore --list (для формата custom .dump)
  MySQL: проверка существования и при необходимости gunzip -t для .sql.gz
  MongoDB: проверка наличия каталога и файлов BSON/metadata
  Redis: проверка существования и размера .rdb
Использование:
  python3 backup_verify.py --type pg --path /backup/pg/pg_mydb_2025-02-11.dump
  python3 backup_verify.py --type mysql --path /backup/mysql/mysql_all_2025-02-11.sql.gz
  python3 backup_verify.py --type redis --path /backup/redis/redis_2025-02-11.rdb
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backup_common import log, run


def verify_pg(path: Path, pg_restore: str) -> int:
    """Проверка дампа PostgreSQL: pg_restore --list."""
    if not path.exists():
        log(f"Файл не найден: {path}")
        return 1
    code = run([pg_restore, "--list", str(path)], log_prefix="[pg_restore --list] ")
    return 0 if code == 0 else 1


def verify_mysql(path: Path) -> int:
    """Проверка: файл существует; если .gz — gunzip -t."""
    if not path.exists():
        log(f"Файл не найден: {path}")
        return 1
    if path.suffix == ".gz" or path.name.endswith(".sql.gz"):
        code = run(["gunzip", "-t", str(path)], log_prefix="[gunzip -t] ")
        return 0 if code == 0 else 1
    if path.stat().st_size == 0:
        log("Файл пустой")
        return 1
    return 0


def verify_mongo(path: Path) -> int:
    """Проверка каталога mongodump: есть подкаталоги с .bson/.metadata.json."""
    if not path.is_dir():
        log(f"Каталог не найден: {path}")
        return 1
    has_bson = False
    for f in path.rglob("*"):
        if f.suffix == ".bson" or f.name.endswith(".metadata.json"):
            has_bson = True
            break
    if not has_bson:
        log("В каталоге нет ожидаемых файлов BSON/metadata")
        return 1
    return 0


def verify_redis(path: Path) -> int:
    """Проверка: файл существует и не пустой."""
    if not path.exists():
        log(f"Файл не найден: {path}")
        return 1
    if path.stat().st_size == 0:
        log("Файл пустой")
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Проверка целостности бэкапов")
    parser.add_argument("--type", "-t", required=True, choices=["pg", "postgres", "mysql", "mongo", "mongodb", "redis"],
                        help="Тип бэкапа")
    parser.add_argument("--path", "-p", required=True, help="Путь к файлу или каталогу бэкапа")
    parser.add_argument("--pg-restore", default="pg_restore", help="Путь к pg_restore (для типа pg)")
    args = parser.parse_args()

    path = Path(args.path)
    t = args.type

    if t in ("pg", "postgres"):
        return verify_pg(path, args.pg_restore)
    if t == "mysql":
        return verify_mysql(path)
    if t in ("mongo", "mongodb"):
        return verify_mongo(path)
    if t == "redis":
        return verify_redis(path)
    return 1


if __name__ == "__main__":
    sys.exit(main())
