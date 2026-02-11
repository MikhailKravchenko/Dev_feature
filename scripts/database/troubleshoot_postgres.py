#!/usr/bin/env python3
"""
Troubleshooting PostgreSQL: версия, соединения, память, репликация.
Подсветка [WARN] при выходе параметров за пороги (соединения близки к max, лаг реплики и т.д.).
Переменные: PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE (по умолчанию postgres).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from db_common import line, line_with_threshold, run_cmd, section

PSQL = "psql"
CONN_ARGS = ["-t", "-A", "-w"]


def conn_args(db: str = "postgres") -> list[str]:
    args = [PSQL] + CONN_ARGS + ["-d", db]
    if os.environ.get("PGHOST"):
        args.extend(["-h", os.environ["PGHOST"]])
    if os.environ.get("PGPORT"):
        args.extend(["-p", str(os.environ["PGPORT"])])
    return args


def query(cmd: list[str], q: str) -> tuple[int, str]:
    return run_cmd(cmd + ["-c", q], timeout=10, env=os.environ)


def main() -> int:
    db = os.environ.get("PGDATABASE", "postgres")
    cmd = conn_args(db)
    code, _ = query(cmd, "SELECT 1")
    if code != 0:
        print("PostgreSQL недоступен (проверьте PGHOST, PGPORT, PGPASSWORD, что сервер запущен).")
        return 1

    section("PostgreSQL — состояние и параметры")

    # Версия
    code, out = query(cmd, "SELECT version();")
    if code == 0 and out:
        line("Версия", out.split("\n")[0][:80])

    # max_connections и текущие соединения
    code, max_conn = query(cmd, "SHOW max_connections;")
    code2, num_conn = query(cmd, "SELECT count(*) FROM pg_stat_activity;")
    try:
        max_c = int(max_conn.strip()) if max_conn else 0
        cur_c = int(num_conn.strip()) if num_conn else 0
        line("Соединения", f"{cur_c} / {max_c}")
        if max_c > 0:
            pct = 100 * cur_c / max_c
            line_with_threshold(
                "  использование лимита соединений, %",
                round(pct, 1),
                "%",
                warn_above=80.0,
            )
    except (ValueError, ZeroDivisionError):
        line("Соединения", f"{num_conn or '?'} / {max_conn or '?'}")

    # Память
    for param in ("shared_buffers", "work_mem", "maintenance_work_mem"):
        code, out = query(cmd, f"SHOW {param};")
        if code == 0 and out:
            line(f"  {param}", out.strip())

    # Репликация
    code, is_replica = query(cmd, "SELECT pg_is_in_recovery();")
    if code == 0 and is_replica and is_replica.strip().lower() == "t":
        line("Роль", "реплика")
        code2, lag = query(cmd, "SELECT coalesce(extract(epoch from (now() - pg_last_xact_replay_timestamp()))::int, 0);")
        try:
            lag_s = int(lag.strip()) if lag else 0
            line_with_threshold("  лаг репликации", lag_s, "сек", warn_above=60)
        except (ValueError, TypeError):
            line("  лаг репликации", lag or "?")
    else:
        line("Роль", "primary (master)")

    # Долгие запросы (> 60 сек)
    code, long_queries = query(cmd, """
        SELECT count(*) FROM pg_stat_activity
        WHERE state = 'active' AND query_start < now() - interval '60 seconds' AND pid != pg_backend_pid();
    """)
    if code == 0 and long_queries:
        try:
            n = int(long_queries.strip())
            line_with_threshold("Долгие запросы (>60 сек)", n, "шт", warn_above=0)
        except ValueError:
            line("Долгие запросы", long_queries or "?")

    # Блокировки (ожидающие)
    code, waiting = query(cmd, "SELECT count(*) FROM pg_stat_activity WHERE wait_event_type = 'Lock';")
    if code == 0 and waiting:
        try:
            n = int(waiting.strip())
            line_with_threshold("Ожидающие блокировку", n, "шт", warn_above=0)
        except ValueError:
            pass

    # Размер БД (текущей)
    code, size = query(cmd, "SELECT pg_database_size(current_database());")
    if code == 0 and size:
        try:
            size_b = int(size.strip())
            size_mb = size_b / (1024 * 1024)
            line("Размер текущей БД", f"{size_mb:.1f} MiB")
        except (ValueError, TypeError):
            line("Размер текущей БД", size or "?")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
