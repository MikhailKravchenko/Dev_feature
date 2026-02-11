#!/usr/bin/env python3
"""
Troubleshooting Redis: версия, клиенты, память, персистентность, репликация.
Подсветка [WARN] при выходе за пороги (память, клиенты, лаг реплики).
Переменные: REDIS_HOST, REDIS_PORT (по умолчанию 127.0.0.1, 6379).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from db_common import line, line_with_threshold, run_cmd, section


def redis_cmd(*args: str) -> list[str]:
    cmd = ["redis-cli"]
    if os.environ.get("REDIS_HOST"):
        cmd.extend(["-h", os.environ["REDIS_HOST"]])
    if os.environ.get("REDIS_PORT"):
        cmd.extend(["-p", str(os.environ["REDIS_PORT"])])
    cmd.extend(args)
    return cmd


def main() -> int:
    code, out = run_cmd(redis_cmd("PING"), timeout=5)
    if code != 0 or (out or "").strip().upper() != "PONG":
        print("Redis недоступен (проверьте REDIS_HOST, REDIS_PORT, что redis-server запущен).")
        return 1

    section("Redis — состояние и параметры")

    # INFO server (версия)
    code, info = run_cmd(redis_cmd("INFO", "server"), timeout=5)
    if code == 0 and info:
        for line_str in info.splitlines():
            if line_str.startswith("redis_version:"):
                line("Версия", line_str.split(":", 1)[1].strip())
                break

    # Клиенты
    code, connected = run_cmd(redis_cmd("INFO", "clients"), timeout=5)
    code2, maxclients = run_cmd(redis_cmd("CONFIG", "GET", "maxclients"), timeout=5)
    try:
        cur_c = 0
        for l in (connected or "").splitlines():
            if l.startswith("connected_clients:"):
                cur_c = int(l.split(":", 1)[1].strip())
                break
        max_c = 10000
        if maxclients:
            parts = maxclients.strip().splitlines()
            if len(parts) >= 2:
                max_c = int(parts[1])
        line("Клиенты", f"{cur_c} / {max_c}")
        if max_c > 0:
            pct = 100 * cur_c / max_c
            line_with_threshold("  использование лимита, %", round(pct, 1), "%", warn_above=80.0)
    except (ValueError, IndexError):
        line("Клиенты", connected or "?")

    # Память
    code, mem_info = run_cmd(redis_cmd("INFO", "memory"), timeout=5)
    if code == 0 and mem_info:
        used = None
        maxmem = None
        for l in mem_info.splitlines():
            if l.startswith("used_memory_human:"):
                line("  used_memory", l.split(":", 1)[1].strip())
            if l.startswith("used_memory:"):
                try:
                    used = int(l.split(":", 1)[1].strip())
                except ValueError:
                    pass
            if l.startswith("maxmemory:"):
                try:
                    maxmem = int(l.split(":", 1)[1].strip())
                except ValueError:
                    pass
        if used is not None and maxmem is not None and maxmem > 0:
            pct = 100 * used / maxmem
            line_with_threshold("  использование maxmemory, %", round(pct, 1), "%", warn_above=90.0)
        elif maxmem == 0:
            line("  maxmemory", "не задан (без лимита)")

    # Персистентность
    code, persist = run_cmd(redis_cmd("INFO", "persistence"), timeout=5)
    if code == 0 and persist:
        for l in persist.splitlines():
            if l.startswith("rdb_last_save_time:"):
                line("  rdb_last_save_time", l.split(":", 1)[1].strip(), "(unixtime)")
            if l.startswith("aof_enabled:"):
                line("  aof_enabled", l.split(":", 1)[1].strip())

    # Репликация (если реплика)
    code, repl = run_cmd(redis_cmd("INFO", "replication"), timeout=5)
    if code == 0 and repl:
        role = None
        for l in repl.splitlines():
            if l.startswith("role:"):
                role = l.split(":", 1)[1].strip()
                line("Роль", role)
                break
        if role == "slave":
            master_link = "unknown"
            lag = None
            for l in repl.splitlines():
                if l.startswith("master_link_status:"):
                    master_link = l.split(":", 1)[1].strip()
                if l.startswith("master_last_io_seconds_ago:"):
                    try:
                        lag = int(l.split(":", 1)[1].strip())
                    except ValueError:
                        pass
            if master_link != "up":
                line("  master_link_status", master_link, is_warn=True)
            if lag is not None:
                line_with_threshold("  master_last_io_seconds_ago", lag, "сек", warn_above=10)

    # Подключённые клиенты (число)
    code, clients = run_cmd(redis_cmd("CLIENT", "LIST"), timeout=5)
    if code == 0 and clients:
        n = len([c for c in clients.splitlines() if c.strip()])
        line("Подключений (CLIENT LIST)", f"{n}")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
