#!/usr/bin/env python3
"""
Troubleshooting MySQL/MariaDB: версия, соединения, InnoDB, репликация.
Подсветка [WARN] при выходе за пороги (соединения, лаг реплики, буфер и т.д.).
Переменные: MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD (или MYSQL_PASSWORD).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from db_common import line, line_with_threshold, run_cmd, section


def mysql_cmd() -> list[str]:
    cmd = ["mysql", "-N", "-e"]
    if os.environ.get("MYSQL_HOST"):
        cmd.extend(["-h", os.environ["MYSQL_HOST"]])
    if os.environ.get("MYSQL_PORT"):
        cmd.extend(["-P", str(os.environ["MYSQL_PORT"])])
    if os.environ.get("MYSQL_USER"):
        cmd.extend(["-u", os.environ["MYSQL_USER"]])
    return cmd


def query(sql: str) -> tuple[int, str]:
    env = os.environ.copy()
    return run_cmd(mysql_cmd() + [sql], timeout=10, env=env)


def main() -> int:
    code, _ = query("SELECT 1")
    if code != 0:
        print("MySQL/MariaDB недоступен (проверьте MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD).")
        return 1

    section("MySQL/MariaDB — состояние и параметры")

    # Версия
    code, out = query("SELECT @@version;")
    if code == 0 and out:
        line("Версия", out.strip()[:80])

    # Соединения
    code, threads = query("SELECT @@max_connections;")
    code2, connected = query("SHOW GLOBAL STATUS LIKE 'Threads_connected';")
    try:
        max_c = int(threads.strip()) if threads else 0
        # Threads_connected value is second column
        cur_c = 0
        if connected:
            parts = connected.split()
            if len(parts) >= 2:
                cur_c = int(parts[1])
        line("Соединения", f"{cur_c} / {max_c}")
        if max_c > 0:
            pct = 100 * cur_c / max_c
            line_with_threshold(
                "  использование лимита соединений, %",
                round(pct, 1),
                "%",
                warn_above=80.0,
            )
    except (ValueError, IndexError, ZeroDivisionError):
        line("Соединения", f"{connected or '?'} / {threads or '?'}")

    # InnoDB buffer pool
    code, bp_size = query("SHOW GLOBAL VARIABLES LIKE 'innodb_buffer_pool_size';")
    if code == 0 and bp_size:
        parts = bp_size.split()
        if len(parts) >= 2:
            try:
                val = int(parts[1])
                line("  innodb_buffer_pool_size", f"{val / (1024**3):.2f} GiB")
            except (ValueError, IndexError):
                line("  innodb_buffer_pool_size", parts[1])
    code, bp_pages = query("SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_pages_data';")
    code2, bp_free = query("SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_pages_free';")
    if bp_pages and bp_free:
        try:
            data = int(bp_pages.split()[1])
            free = int(bp_free.split()[1])
            total = data + free
            if total > 0:
                used_pct = 100 * data / total
                line_with_threshold("  использование buffer pool, %", round(used_pct, 1), "%", warn_above=90.0)
        except (ValueError, IndexError, ZeroDivisionError):
            pass

    # Репликация (если слейв)
    code, slave_io = query("SHOW GLOBAL STATUS LIKE 'Slave_IO_Running';")
    code2, slave_sql = query("SHOW GLOBAL STATUS LIKE 'Slave_SQL_Running';")
    code3, behind = query("SHOW GLOBAL STATUS LIKE 'Seconds_Behind_Master';")
    if slave_io and "Yes" in (slave_io.split()[1] if len(slave_io.split()) >= 2 else ""):
        line("Роль", "реплика (slave)")
        try:
            lag = int(behind.split()[1]) if behind and len(behind.split()) >= 2 else None
            if lag is not None:
                line_with_threshold("  Seconds_Behind_Master", lag, "сек", warn_above=60)
        except (ValueError, IndexError, TypeError):
            line("  Seconds_Behind_Master", behind or "?")
        io_ok = "Yes" in (slave_io.split()[1] if len(slave_io.split()) >= 2 else "")
        sql_ok = "Yes" in (slave_sql.split()[1] if len(slave_sql.split()) >= 2 else "")
        if not io_ok or not sql_ok:
            line("  Slave_IO_Running / Slave_SQL_Running", f"{io_ok} / {sql_ok}", is_warn=True)
    else:
        line("Роль", "primary (master)")

    # Slow queries
    code, slow = query("SHOW GLOBAL STATUS LIKE 'Slow_queries';")
    if code == 0 and slow and len(slow.split()) >= 2:
        try:
            n = int(slow.split()[1])
            line_with_threshold("Медленные запросы (накоплено)", n, "шт", warn_above=100)
        except (ValueError, IndexError):
            pass

    # Открытые таблицы
    code, open_t = query("SHOW GLOBAL STATUS LIKE 'Open_tables';")
    code2, max_t = query("SHOW GLOBAL VARIABLES LIKE 'table_open_cache';")
    if open_t and max_t:
        try:
            ot = int(open_t.split()[1])
            mt = int(max_t.split()[1])
            line("Открытые таблицы", f"{ot} / {mt}")
            if mt > 0:
                line_with_threshold("  использование table_open_cache, %", round(100 * ot / mt, 1), "%", warn_above=80.0)
        except (ValueError, IndexError, ZeroDivisionError):
            pass

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
