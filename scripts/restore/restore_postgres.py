#!/usr/bin/env python3
"""
Восстановление PostgreSQL из бэкапа (формат custom .dump или directory).
Опционально: создание БД (createdb), очистка объектов перед восстановлением (--clean).
Переменные: PGHOST, PGPORT, PGUSER, PGPASSWORD.
Использование:
  python3 restore_postgres.py --backup /path/to/file.dump --database mydb [--create-db] [--clean]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], env: dict | None = None) -> int:
    print(f"  Выполняется: {' '.join(cmd)}", file=sys.stderr)
    try:
        r = subprocess.run(cmd, env={**os.environ, **(env or {})}, timeout=3600)
        return r.returncode
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"  Ошибка: {e}", file=sys.stderr)
        return -1


def main() -> int:
    parser = argparse.ArgumentParser(description="Восстановление PostgreSQL из бэкапа (pg_restore)")
    parser.add_argument("--backup", "-b", required=True, help="Путь к файлу .dump (custom) или каталогу (directory format)")
    parser.add_argument("--database", "-d", required=True, help="Имя целевой БД")
    parser.add_argument("--create-db", action="store_true", help="Создать БД перед восстановлением (createdb)")
    parser.add_argument("--clean", action="store_true", help="Удалить объекты перед восстановлением (pg_restore --clean)")
    parser.add_argument("--no-owner", action="store_true", default=True, help="Не восстанавливать владельцев (по умолчанию включено)")
    parser.add_argument("--pg-restore", default="pg_restore", help="Путь к pg_restore")
    parser.add_argument("--createdb", default="createdb", help="Путь к createdb")
    args = parser.parse_args()

    backup = Path(args.backup)
    if not backup.exists():
        print(f"Ошибка: бэкап не найден: {backup}", file=sys.stderr)
        return 1

    db = args.database
    cmd_base = [args.pg_restore, "-d", db]
    if os.environ.get("PGHOST"):
        cmd_base.extend(["-h", os.environ["PGHOST"]])
    if os.environ.get("PGPORT"):
        cmd_base.extend(["-p", str(os.environ["PGPORT"])])
    if os.environ.get("PGUSER"):
        cmd_base.extend(["-U", os.environ["PGUSER"]])

    if args.create_db:
        print("Создание БД...", file=sys.stderr)
        create_cmd = [args.createdb, db]
        if os.environ.get("PGHOST"):
            create_cmd.extend(["-h", os.environ["PGHOST"]])
        if os.environ.get("PGPORT"):
            create_cmd.extend(["-p", str(os.environ["PGPORT"])])
        if os.environ.get("PGUSER"):
            create_cmd.extend(["-U", os.environ["PGUSER"]])
        code = run(create_cmd)
        if code != 0:
            # БД может уже существовать
            print("  (createdb завершился с ошибкой; продолжаем восстановление)", file=sys.stderr)

    cmd = cmd_base + [str(backup)]
    if args.clean:
        cmd.insert(cmd.index("-d") + 2, "--clean")
    if args.no_owner:
        cmd.insert(cmd.index("-d") + 2, "--no-owner")

    print("Восстановление...", file=sys.stderr)
    code = run(cmd)
    if code != 0:
        return code
    print("Готово.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
