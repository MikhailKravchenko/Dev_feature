#!/usr/bin/env python3
"""
Восстановление MySQL/MariaDB из дампа (.sql или .sql.gz).
Переменные: MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD.
Использование:
  python3 restore_mysql.py --backup /path/to/dump.sql.gz [--database mydb]
  Если в дампе одна БД или --all-databases, --database можно не указывать.
"""
from __future__ import annotations

import argparse
import gzip
import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], stdin=None, env: dict | None = None) -> int:
    print(f"  Выполняется: {' '.join(cmd[:6])}{'...' if len(cmd) > 6 else ''}", file=sys.stderr)
    try:
        r = subprocess.run(
            cmd,
            stdin=stdin,
            env={**os.environ, **(env or {})},
            timeout=7200,
        )
        return r.returncode
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"  Ошибка: {e}", file=sys.stderr)
        return -1


def main() -> int:
    parser = argparse.ArgumentParser(description="Восстановление MySQL/MariaDB из дампа")
    parser.add_argument("--backup", "-b", required=True, help="Путь к .sql или .sql.gz")
    parser.add_argument("--database", "-d", default=None, help="Целевая БД (опционально; для дампа одной БД можно не указывать)")
    parser.add_argument("--mysql", default="mysql", help="Путь к mysql")
    args = parser.parse_args()

    backup = Path(args.backup)
    if not backup.exists():
        print(f"Ошибка: бэкап не найден: {backup}", file=sys.stderr)
        return 1

    cmd = [args.mysql]
    if os.environ.get("MYSQL_HOST"):
        cmd.extend(["-h", os.environ["MYSQL_HOST"]])
    if os.environ.get("MYSQL_PORT"):
        cmd.extend(["-P", str(os.environ["MYSQL_PORT"])])
    if os.environ.get("MYSQL_USER"):
        cmd.extend(["-u", os.environ["MYSQL_USER"]])
    if args.database:
        cmd.extend([args.database])

    env = os.environ.copy()
    if os.environ.get("MYSQL_PWD") or os.environ.get("MYSQL_PASSWORD"):
        env["MYSQL_PWD"] = os.environ.get("MYSQL_PWD") or os.environ.get("MYSQL_PASSWORD", "")

    if backup.suffix == ".gz" or backup.name.endswith(".sql.gz"):
        print("Распаковка и восстановление (gunzip | mysql)...", file=sys.stderr)
        try:
            with gzip.open(backup, "rb") as f:
                code = run(cmd, stdin=f, env=env)
        except OSError as e:
            print(f"Ошибка чтения gzip: {e}", file=sys.stderr)
            return 1
    else:
        print("Восстановление из .sql (mysql < file)...", file=sys.stderr)
        with open(backup, "rb") as f:
            code = run(cmd, stdin=f, env=env)

    if code != 0:
        return code
    print("Готово.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
