#!/usr/bin/env python3
"""
Восстановление MongoDB из дампа (каталог mongodump).
Переменные: MONGODB_URI или MONGODB_HOST, MONGODB_PORT.
Использование:
  python3 restore_mongodb.py --backup /path/to/mongo_YYYY-MM-DD_HH-MM [--drop] [--gzip]
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
        r = subprocess.run(cmd, env={**os.environ, **(env or {})}, timeout=7200)
        return r.returncode
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"  Ошибка: {e}", file=sys.stderr)
        return -1


def main() -> int:
    parser = argparse.ArgumentParser(description="Восстановление MongoDB из дампа (mongorestore)")
    parser.add_argument("--backup", "-b", required=True, help="Путь к каталогу дампа (результат mongodump)")
    parser.add_argument("--drop", action="store_true", help="Удалять коллекции перед восстановлением")
    parser.add_argument("--gzip", action="store_true", help="Дамп был создан с --gzip (mongorestore --gzip)")
    parser.add_argument("--mongorestore", default="mongorestore", help="Путь к mongorestore")
    args = parser.parse_args()

    backup = Path(args.backup)
    if not backup.is_dir():
        print(f"Ошибка: каталог дампа не найден: {backup}", file=sys.stderr)
        return 1

    cmd = [args.mongorestore, str(backup)]
    if os.environ.get("MONGODB_URI"):
        cmd.extend(["--uri", os.environ["MONGODB_URI"]])
    else:
        if os.environ.get("MONGODB_HOST"):
            cmd.extend(["--host", os.environ["MONGODB_HOST"]])
        if os.environ.get("MONGODB_PORT"):
            cmd.extend(["--port", os.environ["MONGODB_PORT"]])
    if args.drop:
        cmd.append("--drop")
    if args.gzip:
        cmd.append("--gzip")

    print("Восстановление (mongorestore)...", file=sys.stderr)
    code = run(cmd)
    if code != 0:
        return code
    print("Готово.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
