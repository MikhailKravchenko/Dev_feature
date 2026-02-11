#!/usr/bin/env python3
"""
Бэкап MySQL / MariaDB: mysqldump. Одна БД или все (--all-databases).
Сжатие: gzip. Переменные окружения: MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD (или --password).
Использование:
  python3 backup_mysql.py --dest /backup/mysql [--database NAME] [--all-databases] [--rotate-days N] [--no-gzip]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backup_common import dated_path, log, rotate_by_days, run


def main() -> int:
    parser = argparse.ArgumentParser(description="Бэкап MySQL/MariaDB (mysqldump)")
    parser.add_argument("--dest", required=True, help="Каталог для сохранения бэкапов")
    parser.add_argument("--database", "-d", default=None, help="Имя БД (если не указано при одном бэкапе — из MYSQL_DATABASE)")
    parser.add_argument("--all-databases", action="store_true", help="Бэкап всех БД")
    parser.add_argument("--rotate-days", type=int, default=0, help="Удалить бэкапы старше N дней")
    parser.add_argument("--no-gzip", action="store_true", help="Не сжимать вывод (по умолчанию gzip)")
    parser.add_argument("--mysqldump", default="mysqldump", help="Путь к mysqldump")
    parser.add_argument("--host", default=os.environ.get("MYSQL_HOST"), help="Хост (или MYSQL_HOST)")
    parser.add_argument("--port", default=os.environ.get("MYSQL_PORT", "3306"), help="Порт")
    parser.add_argument("--user", "-u", default=os.environ.get("MYSQL_USER"), help="Пользователь (или MYSQL_USER)")
    parser.add_argument("--password", "-p", default=os.environ.get("MYSQL_PWD") or os.environ.get("MYSQL_PASSWORD"), help="Пароль (лучше MYSQL_PWD)")
    args = parser.parse_args()

    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    if args.password:
        env["MYSQL_PWD"] = args.password

    cmd = [args.mysqldump, "--single-transaction", "--routines", "--triggers", "--events"]
    if args.host:
        cmd.extend(["--host", args.host])
    if args.port:
        cmd.extend(["--port", str(args.port)])
    if args.user:
        cmd.extend(["--user", args.user])

    use_gzip = not args.no_gzip
    suffix = ".sql.gz" if use_gzip else ".sql"

    if args.all_databases:
        out_path = dated_path(dest, "mysql_all", suffix)
        log(f"Бэкап всех БД в {out_path}")
        cmd.append("--all-databases")
        prefix_rotate = "mysql_all_"
    else:
        db = args.database or os.environ.get("MYSQL_DATABASE", "mysql")
        out_path = dated_path(dest, f"mysql_{db}", suffix)
        log(f"Бэкап БД {db} в {out_path}")
        cmd.append(db)
        prefix_rotate = f"mysql_{db}_"

    if use_gzip:
        sql_path = out_path.with_suffix("")  # .sql.gz -> .sql
        cmd.extend(["--result-file", str(sql_path)])
        code = run(cmd, env=env, log_prefix="[mysqldump] ")
        if code != 0:
            if sql_path.exists():
                sql_path.unlink(missing_ok=True)
            return code
        code = run(["gzip", "-f", str(sql_path)], log_prefix="[gzip] ")
        if code != 0:
            sql_path.unlink(missing_ok=True)
            return code
        # gzip -f создаёт sql_path.gz; имя out_path уже .sql.gz, совпадает
    else:
        cmd.extend(["--result-file", str(out_path)])
        code = run(cmd, env=env, log_prefix="[mysqldump] ")
        if code != 0:
            return code

    if args.rotate_days > 0:
        rotate_by_days(dest, prefix_rotate, args.rotate_days)

    log("Готово.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
