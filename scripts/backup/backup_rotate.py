#!/usr/bin/env python3
"""
Ротация бэкапов: удаление старых по возрасту (--days) или оставить только последние N (--keep).
Использование:
  python3 backup_rotate.py --dir /backup/pg --prefix pg_mydb_ [--days 7]
  python3 backup_rotate.py --dir /backup/pg --prefix pg_mydb_ --keep 10
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backup_common import log, rotate_by_days, rotate_keep_n


def main() -> int:
    parser = argparse.ArgumentParser(description="Ротация бэкапов по возрасту или количеству")
    parser.add_argument("--dir", "--directory", dest="directory", required=True, help="Каталог с бэкапами")
    parser.add_argument("--prefix", required=True, help="Префикс имён файлов (например pg_mydb_)")
    parser.add_argument("--days", type=int, default=0, help="Удалить файлы старше N дней")
    parser.add_argument("--keep", type=int, default=0, help="Оставить только последние N файлов")
    args = parser.parse_args()

    dest = Path(args.directory)
    if not dest.is_dir():
        log(f"Ошибка: каталог не найден: {dest}")
        return 1

    if args.days > 0:
        rotate_by_days(dest, args.prefix, args.days)
    if args.keep > 0:
        rotate_keep_n(dest, args.prefix, args.keep)
    if args.days <= 0 and args.keep <= 0:
        log("Укажите --days N или --keep N")
        return 1

    log("Готово.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
