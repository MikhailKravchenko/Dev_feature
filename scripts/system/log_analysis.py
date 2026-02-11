#!/usr/bin/env python3
"""
Анализ логов: поиск ошибок, частых сообщений; проверка наличия конфигов ротации.
Только стандартная библиотека Python. Linux/Ubuntu.
Использование:
  python3 log_analysis.py [файл_или_каталог] [--journal] [--top N] [--pattern PAT]
  --journal   использовать journalctl -p err (последние сообщения уровня error и выше)
  --top N     вывести топ N частых строк (по умолчанию 10)
  --pattern   свой паттерн для поиска (по умолчанию ERROR|CRITICAL|Fail|FAIL|error)
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

DEFAULT_PATTERN = r"ERROR|CRITICAL|Fail|FAIL|error|WARN|Warning"
LOGROTATE_CONFIGS = ["/etc/logrotate.conf", "/etc/logrotate.d"]


def journal_err(lines: int = 100) -> str:
    """Читает journalctl -p err -n N (без пагинации)."""
    try:
        r = subprocess.run(
            ["journalctl", "-p", "err", "-n", str(lines), "--no-pager"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return r.stdout.strip() if r.returncode == 0 else f"Ошибка journalctl: код {r.returncode}"
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return str(e)


def scan_file(path: Path, pattern: re.Pattern[str]) -> list[str]:
    """Возвращает строки, совпадающие с pattern. Кодировки: utf-8, latin-1."""
    matches = []
    for enc in ("utf-8", "latin-1", "cp1251"):
        try:
            text = path.read_text(encoding=enc, errors="replace")
            for line in text.splitlines():
                if pattern.search(line):
                    matches.append(line.strip()[:200])  # ограничить длину
            return matches
        except (OSError, UnicodeDecodeError):
            continue
    return matches


def scan_path(path: Path, pattern: re.Pattern[str], max_files: int = 50) -> list[str]:
    """Рекурсивно сканирует файлы .log и без расширения в каталоге."""
    matches = []
    if path.is_file():
        return scan_file(path, pattern)
    if not path.is_dir():
        return []
    count = 0
    for f in sorted(path.iterdir()):
        if count >= max_files:
            break
        if f.is_file() and (f.suffix == ".log" or f.name.startswith("log")):
            matches.extend(scan_file(f, pattern))
            count += 1
        elif f.is_dir():
            matches.extend(scan_path(f, pattern, max_files - count))
            count += 1
    return matches


def top_lines(lines: list[str], n: int) -> list[tuple[str, int]]:
    """Топ N самых частых строк (нормализованных: без дат/цифр по желанию можно оставить как есть)."""
    normalized = []
    for line in lines:
        s = line.strip()
        if len(s) > 5:
            normalized.append(s)
    return Counter(normalized).most_common(n)


def logrotate_info() -> list[str]:
    """Проверка наличия конфигов logrotate (ротация логов)."""
    result = []
    p = Path(LOGROTATE_CONFIGS[0])
    if p.exists():
        result.append(f"  {p} существует")
    d = Path(LOGROTATE_CONFIGS[1])
    if d.is_dir():
        count = len(list(d.iterdir()))
        result.append(f"  {d}: {count} конфигов")
    return result if result else ["  конфиги logrotate не проверялись"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Анализ логов: ошибки, частые сообщения, ротация")
    parser.add_argument("path", nargs="?", default=None, help="Файл или каталог с логами")
    parser.add_argument("--journal", action="store_true", help="Вывести journalctl -p err")
    parser.add_argument("--top", type=int, default=10, help="Топ N частых строк")
    parser.add_argument("--pattern", default=DEFAULT_PATTERN, help="Регулярное выражение для поиска")
    parser.add_argument("--rotation", action="store_true", help="Показать информацию о logrotate")
    args = parser.parse_args()

    pattern = re.compile(args.pattern, re.IGNORECASE)

    if args.journal:
        print("=== journalctl -p err (последние 100) ===")
        print(journal_err(100))
        print()

    if args.path:
        p = Path(args.path)
        if not p.exists():
            print(f"Путь не найден: {p}", file=sys.stderr)
            sys.exit(1)
        matches = scan_path(p, pattern)
        print(f"=== Совпадения по паттерну в {p} (всего {len(matches)} строк) ===")
        for line in matches[:100]:
            print(line)
        if len(matches) > 100:
            print(f"... и ещё {len(matches) - 100} строк")
        print()
        if matches and args.top > 0:
            print(f"--- Топ {args.top} частых строк ---")
            for line, cnt in top_lines(matches, args.top):
                print(f"  {cnt:>5}  {line[:120]}")
        print()

    if args.rotation:
        print("=== Ротация логов (logrotate) ===")
        for line in logrotate_info():
            print(line)
        print()

    if not args.journal and not args.path and not args.rotation:
        print("Укажите --journal, путь к логам или --rotation. Справка: -h", file=sys.stderr)
        sys.exit(1)

    print("================================")


if __name__ == "__main__":
    main()
