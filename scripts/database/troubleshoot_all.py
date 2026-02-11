#!/usr/bin/env python3
"""
Единая точка входа: определить запущенные СУБД и для каждой вывести состояние и параметры
с подсветкой выхода за пороги. Запускает detect_databases.py и затем troubleshoot_* для каждой обнаруженной БД.
Использование: python3 troubleshoot_all.py [--only pg|mysql|mongo|redis]
"""
from __future__ import annotations

import argparse
import socket
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def port_open(host: str, port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            return s.connect_ex((host, port)) == 0
    except OSError:
        return False


def run_script(name: str) -> int:
    """Запуск скрипта в этой же папке. Возвращает код выхода."""
    path = SCRIPT_DIR / name
    if not path.exists():
        return -1
    r = subprocess.run([sys.executable, str(path)], timeout=60)
    return r.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Troubleshooting всех обнаруженных СУБД")
    parser.add_argument("--only", choices=["pg", "mysql", "mongo", "redis"], help="Проверить только указанную СУБД")
    parser.add_argument("--host", default="127.0.0.1", help="Хост для определения портов")
    args = parser.parse_args()

    if args.only:
        mapping = {
            "pg": "troubleshoot_postgres.py",
            "mysql": "troubleshoot_mysql.py",
            "mongo": "troubleshoot_mongodb.py",
            "redis": "troubleshoot_redis.py",
        }
        return run_script(mapping[args.only])

    # Определяем, что запущено
    to_run = []
    if port_open(args.host, 5432):
        to_run.append(("PostgreSQL", "troubleshoot_postgres.py"))
    if port_open(args.host, 3306):
        to_run.append(("MySQL/MariaDB", "troubleshoot_mysql.py"))
    if port_open(args.host, 27017):
        to_run.append(("MongoDB", "troubleshoot_mongodb.py"))
    if port_open(args.host, 6379):
        to_run.append(("Redis", "troubleshoot_redis.py"))

    if not to_run:
        print("Не обнаружено ни одной СУБД на портах 5432, 3306, 27017, 6379.")
        return 0

    exit_code = 0
    for label, script in to_run:
        print(f"\n{'='*60}\n  {label}\n{'='*60}")
        code = run_script(script)
        if code != 0:
            exit_code = code
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
