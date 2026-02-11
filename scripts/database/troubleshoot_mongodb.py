#!/usr/bin/env python3
"""
Troubleshooting MongoDB: версия, соединения, память, репликация (replica set).
Подсветка [WARN] при выходе за пороги.
Переменные: MONGODB_URI или MONGODB_HOST, MONGODB_PORT.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from db_common import line, line_with_threshold, run_cmd, section


def mongosh_cmd() -> list[str]:
    cmd = ["mongosh"]
    uri = os.environ.get("MONGODB_URI")
    if uri:
        cmd.append(uri)
    else:
        host = os.environ.get("MONGODB_HOST", "localhost")
        port = os.environ.get("MONGODB_PORT", "27017")
        cmd.extend(["--host", host, "--port", port])
    cmd.append("--quiet")
    return cmd


def run_js(js: str) -> tuple[int, str]:
    """Выполнить JavaScript в mongosh. Возвращает (code, stdout)."""
    try:
        r = subprocess.run(
            mongosh_cmd() + ["--eval", js],
            capture_output=True,
            text=True,
            timeout=15,
            env=os.environ,
        )
        return (r.returncode, (r.stdout or "").strip())
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return (-1, str(e))


def main() -> int:
    code, out = run_js("db.adminCommand('ping')")
    if code != 0 or "ok" not in (out or "").lower():
        # Попробуем mongo (старый клиент)
        code2, out2 = run_cmd(["mongo", "--quiet", "--eval", "db.adminCommand('ping')"], timeout=15)
        if code2 != 0:
            print("MongoDB недоступен (проверьте MONGODB_URI или MONGODB_HOST/MONGODB_PORT, что mongod запущен).")
            return 1
        # Используем mongo для остальных команд
        def run_js_fallback(js: str) -> tuple[int, str]:
            return run_cmd(["mongo", "--quiet", "--eval", js], timeout=15)
        run_js = run_js_fallback

    section("MongoDB — состояние и параметры")

    # Версия
    code, out = run_js("db.version()")
    if code == 0 and out:
        line("Версия", out.strip())

    # serverStatus (основные метрики)
    code, out = run_js("JSON.stringify(db.serverStatus())")
    if code != 0 or not out:
        line("serverStatus", "не получен")
        print()
        return 0
    try:
        st = json.loads(out)
    except json.JSONDecodeError:
        line("serverStatus", "ошибка разбора JSON")
        print()
        return 0

    # Соединения
    conn = st.get("connections") or {}
    current = conn.get("current")
    available = conn.get("available")
    if current is not None:
        line("Соединения current", str(current))
    if available is not None and current is not None:
        total = current + available
        if total > 0:
            pct = 100 * current / total
            line_with_threshold("  использование соединений, %", round(pct, 1), "%", warn_above=80.0)

    # Память (resident, virtual в MB)
    mem = st.get("mem") or {}
    resident = mem.get("resident")
    virtual = mem.get("virtual")
    if resident is not None:
        line("Память resident", f"{resident} MiB")
    if virtual is not None:
        line("  virtual", f"{virtual} MiB")
    # WiredTiger cache (если есть)
    wt = st.get("wiredTiger", {}).get("cache")
    if wt:
        bytes_max = wt.get("maximum bytes configured", 0)
        bytes_cur = wt.get("bytes currently in the cache", 0)
        if bytes_max > 0:
            pct = 100 * bytes_cur / bytes_max
            line_with_threshold("  кэш WiredTiger, %", round(pct, 1), "%", warn_above=90.0)

    # Репликация
    repl = st.get("repl") or {}
    if repl.get("setName"):
        line("Replica set", repl.get("setName", "?"))
        is_primary = repl.get("ismaster") or repl.get("isWritablePrimary")
        line("  роль", "primary" if is_primary else "secondary")
        if not is_primary and "optimeDate" in repl:
            # Лаг можно оценить по lastOpTime и т.д. — упрощённо
            line("  optimeDate", str(repl.get("optimeDate", "?")))
    else:
        line("Режим", "standalone")

    # Очередь операций (глобальный lock)
    global_lock = st.get("globalLock") or {}
    current_queue = global_lock.get("currentQueue", {})
    total_queued = (current_queue.get("total", 0) or 0) + (current_queue.get("readers", 0) or 0) + (current_queue.get("writers", 0) or 0)
    if total_queued > 0:
        line_with_threshold("Очередь операций (globalLock)", total_queued, "шт", warn_above=10)

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
