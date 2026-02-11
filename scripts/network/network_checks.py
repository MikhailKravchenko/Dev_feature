#!/usr/bin/env python3
"""
Сетевые проверки: порты (слушающие), соединения, DNS, базовая HTTP-проверка.
Только стандартная библиотека Python. Linux/Ubuntu (для портов/соединений вызывается ss).
Использование:
  python3 network_checks.py [--ports] [--connections] [--dns ИМЯ] [--http URL]
  Без аргументов выводит сводку: порты + кратко соединения.
"""
from __future__ import annotations

import argparse
import socket
import subprocess
import sys
import urllib.request
from urllib.error import URLError

# Таймаут для HTTP и DNS (секунды)
TIMEOUT = 10


def run_ss(*args: str) -> str:
    """Вызов ss (socket statistics). Команда: показываем слушающие порты и соединения без резолва."""
    cmd = ["ss", "-tuln"] + list(args)
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        return f"Ошибка выполнения ss: {e}"


def run_ss_established() -> str:
    """Активные TCP-соединения (established)."""
    try:
        r = subprocess.run(
            ["ss", "-tn", "state", "established"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return r.stdout.strip() if r.returncode == 0 else f"код выхода: {r.returncode}"
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return f"Ошибка: {e}"


def check_dns(name: str) -> str:
    """Резолв имени в IP через getaddrinfo."""
    try:
        results = socket.getaddrinfo(name, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        ips = []
        seen = set()
        for r in results:
            addr = r[4][0]
            if addr not in seen:
                seen.add(addr)
                ips.append(addr)
        return ", ".join(ips) if ips else "адреса не найдены"
    except socket.gaierror as e:
        return f"Ошибка DNS: {e}"
    except Exception as e:
        return f"Ошибка: {e}"


def check_http(url: str) -> str:
    """HEAD или GET запрос, возвращает код и кратко статус."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return f"HTTP {resp.status} ({resp.reason})"
    except URLError as e:
        return f"Ошибка: {e.reason}"
    except Exception as e:
        return f"Ошибка: {e}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Сетевые проверки: порты, соединения, DNS, HTTP")
    parser.add_argument("--ports", action="store_true", help="Показать слушающие порты (ss -tuln)")
    parser.add_argument("--connections", action="store_true", help="Показать установленные TCP-соединения")
    parser.add_argument("--dns", metavar="NAME", help="Резолв имени в IP")
    parser.add_argument("--http", metavar="URL", help="Проверить доступность URL (HEAD)")
    args = parser.parse_args()

    # Если ничего не выбрано — выводим порты и кратко соединения
    if not any([args.ports, args.connections, args.dns, args.http]):
        args.ports = True
        args.connections = True

    if args.ports:
        print("=== Слушающие порты (ss -tuln) ===")
        print(run_ss())
        print()

    if args.connections:
        print("=== Установленные TCP-соединения (established) ===")
        out = run_ss_established()
        lines = out.splitlines()
        if len(lines) > 15:
            print("\n".join(lines[:15]))
            print(f"... и ещё {len(lines) - 15} строк")
        else:
            print(out)
        print()

    if args.dns:
        print(f"=== DNS: {args.dns} ===")
        print(check_dns(args.dns))
        print()

    if args.http:
        print(f"=== HTTP: {args.http} ===")
        print(check_http(args.http))
        print()

    print("================================")


if __name__ == "__main__":
    main()
