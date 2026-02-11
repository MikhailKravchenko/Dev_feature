#!/usr/bin/env python3
"""
Определение, какие СУБД запущены на сервере: проверка портов и опционально systemd.
Выводит список обнаруженных БД (PostgreSQL, MySQL/MariaDB, MongoDB, Redis) и их порты.
Использование: python3 detect_databases.py [--verbose]
"""
from __future__ import annotations

import argparse
import socket
import subprocess
import sys
from pathlib import Path

# Порты по умолчанию и имена для вывода
DB_PORTS = [
    (5432, "PostgreSQL"),
    (3306, "MySQL/MariaDB"),
    (27017, "MongoDB"),
    (6379, "Redis"),
]


def port_listening(host: str, port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            return s.connect_ex((host, port)) == 0
    except OSError:
        return False


def systemd_service(name_pattern: str) -> str | None:
    """Проверяет, есть ли активный systemd-юнит с таким паттерном (postgresql, mysql, mongod, redis)."""
    try:
        r = subprocess.run(
            ["systemctl", "is-active", name_pattern],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip() == "active":
            return r.stdout.strip()
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Определение запущенных СУБД на сервере")
    parser.add_argument("--host", default="127.0.0.1", help="Хост для проверки портов")
    parser.add_argument("--verbose", "-v", action="store_true", help="Вывести также проверку systemd")
    args = parser.parse_args()

    print("=== Обнаруженные СУБД (проверка портов) ===\n")
    found = []
    for port, name in DB_PORTS:
        if port_listening(args.host, port):
            status = f"порт {port} открыт"
            if args.verbose:
                # Попытка сопоставить с systemd (не все дистрибутивы используют те же имена)
                if port == 5432:
                    svc = systemd_service("postgresql") or systemd_service("postgresql@*")
                elif port == 3306:
                    svc = systemd_service("mysql") or systemd_service("mariadb")
                elif port == 27017:
                    svc = systemd_service("mongod")
                elif port == 6379:
                    svc = systemd_service("redis") or systemd_service("redis-server")
                else:
                    svc = None
                if svc:
                    status += f", systemd: {svc}"
            print(f"  [OK] {name} — {status}")
            found.append((port, name))
        else:
            if args.verbose:
                print(f"  —    {name} — порт {port} закрыт")
    if not found:
        print("  Не обнаружено ни одной СУБД на указанном хосте.")
    print("\n================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
