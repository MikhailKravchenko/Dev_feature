#!/usr/bin/env python3
"""
Проверка сервисов systemd: статус, перезапуски, failed-юниты, опционально зависимости.
Только стандартная библиотека Python. Вызов systemctl. Linux/Ubuntu.
Использование:
  python3 systemd_services.py [--failed] [--restarts] [--list] [--unit NAME]
  --failed   показать только неактивные/failed юниты
  --restarts показать юниты с перезапусками (Requires полагаемся на systemctl show)
  --list     список загруженных unit-файлов (сервисы)
  --unit     статус и зависимости одного юнита
"""
from __future__ import annotations

import argparse
import subprocess
import sys


def run_systemctl(*args: str, timeout: int = 15) -> tuple[str, int]:
    """Запуск systemctl. Возвращает (stdout, returncode)."""
    try:
        r = subprocess.run(
            ["systemctl", "--no-pager", "--no-legend"] + list(args),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return (r.stdout.strip(), r.returncode)
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return (str(e), -1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Проверка сервисов systemd")
    parser.add_argument("--failed", action="store_true", help="Показать failed и неактивные юниты")
    parser.add_argument("--restarts", action="store_true", help="Показать юниты с перезапусками (NRestarts)")
    parser.add_argument("--list", action="store_true", help="Список загруженных сервисов (тип service)")
    parser.add_argument("--unit", metavar="NAME", help="Статус и зависимости одного юнита")
    args = parser.parse_args()

    # По умолчанию показываем общий статус и failed
    if not any([args.failed, args.restarts, args.list, args.unit]):
        args.failed = True

    if args.unit:
        print(f"=== Статус и зависимости: {args.unit} ===")
        out, code = run_systemctl("show", args.unit, "--property=LoadState,ActiveState,SubState,UnitFileState")
        if code != 0:
            print(out or "Юнит не найден или ошибка")
        else:
            print(out)
        print("\n--- Зависимости (Requires) ---")
        out2, _ = run_systemctl("list-dependencies", args.unit, "--plain")
        print(out2 or "(нет вывода)")
        print("================================")
        return

    if args.failed:
        print("=== Failed и неактивные юниты (systemctl --failed) ===")
        out, _ = run_systemctl("--failed")
        if out:
            print(out)
        else:
            print("(пусто — failed юнитов нет)")
        print()

    if args.restarts:
        print("=== Юниты с перезапусками (активные сервисы, показ NRestarts через show) ===")
        out, _ = run_systemctl("list-units", "type=service", "state=active", "--plain")
        if not out:
            print("(нет активных сервисов или ошибка)")
        else:
            for line in out.splitlines():
                unit = line.split()[0] if line.split() else ""
                if not unit.endswith(".service"):
                    continue
                info, _ = run_systemctl("show", unit, "--property=NRestarts,ActiveState")
                if "NRestarts=" in info:
                    for prop in info.splitlines():
                        if prop.startswith("NRestarts="):
                            n = prop.split("=", 1)[1].strip()
                            if n != "0":
                                print(f"  {unit}: перезапусков = {n}")
        print()

    if args.list:
        print("=== Загруженные сервисы (list-units type=service) ===")
        out, _ = run_systemctl("list-units", "type=service", "--plain")
        print(out or "(нет вывода)")
        print()

    print("================================")


if __name__ == "__main__":
    main()
