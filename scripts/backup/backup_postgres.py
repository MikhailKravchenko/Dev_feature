#!/usr/bin/env python3
"""
Бэкап PostgreSQL: pg_dump (одна БД) или pg_dumpall (все БД).
Формат: custom (-Fc) для сжатия и последующей проверки pg_restore --list.
Переменные окружения: PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE (для одной БД).
Использование:
  python3 backup_postgres.py --dest /backup/pg [--database NAME] [--all] [--rotate-days N]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Добавляем путь к общему модулю (текущая папка)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from backup_common import dated_path, log, run


def main() -> int:
    parser = argparse.ArgumentParser(description="Бэкап PostgreSQL (pg_dump / pg_dumpall)")
    parser.add_argument("--dest", required=True, help="Каталог для сохранения бэкапов")
    parser.add_argument("--database", "-d", default=None, help="Имя БД (если не указано — из PGDATABASE или все при --all)")
    parser.add_argument("--all", action="store_true", help="Бэкап всех БД (pg_dumpall), один файл")
    parser.add_argument("--rotate-days", type=int, default=0, help="Удалить бэкапы старше N дней (0 = не удалять)")
    parser.add_argument("--pg-dump", default="pg_dump", help="Путь к pg_dump")
    parser.add_argument("--pg-dumpall", default="pg_dumpall", help="Путь к pg_dumpall")
    args = parser.parse_args()

    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    if args.all:
        out_path = dated_path(dest, "pg_all", ".sql")
        log(f"Бэкап всех БД в {out_path}")
        cmd = [args.pg_dumpall, "--no-owner", "--no-acl", "-f", str(out_path)]
        code = run(cmd, log_prefix="[pg_dumpall] ")
        if code != 0:
            return code
        prefix_rotate = "pg_all_"
    else:
        db = args.database or os.environ.get("PGDATABASE", "postgres")
        out_path = dated_path(dest, f"pg_{db}", ".dump")
        log(f"Бэкап БД {db} в {out_path}")
        cmd = [args.pg_dump, "-Fc", "--no-owner", "--no-acl", "-f", str(out_path), db]
        code = run(cmd, log_prefix="[pg_dump] ")
        if code != 0:
            return code
        prefix_rotate = f"pg_{db}_"

    if args.rotate_days > 0:
        from backup_common import rotate_by_days
        rotate_by_days(dest, prefix_rotate, args.rotate_days)

    log("Готово.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
