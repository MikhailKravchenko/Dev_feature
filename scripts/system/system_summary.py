#!/usr/bin/env python3
"""
Сводка по системе: CPU, RAM, диск, load average, uptime.
Только стандартная библиотека Python. Ориентировано на Linux (Ubuntu).
Вывод: краткая сводка в читаемом виде для быстрой диагностики.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROC = Path("/proc")
PROC_MEMINFO = PROC / "meminfo"
PROC_LOADAVG = PROC / "loadavg"
PROC_UPTIME = PROC / "uptime"
PROC_CPUINFO = PROC / "cpuinfo"
PROC_STAT = PROC / "stat"


def _read_proc(path: Path) -> str:
    try:
        return path.read_text().strip()
    except (OSError, FileNotFoundError) as e:
        return f"<ошибка: {e}>"


def get_load_average() -> str:
    """Читает /proc/loadavg: load average за 1, 5, 15 минут."""
    s = _read_proc(PROC_LOADAVG)
    if s.startswith("<"):
        return s
    parts = s.split()
    if len(parts) >= 3:
        return f"{parts[0]} {parts[1]} {parts[2]} (1m, 5m, 15m)"
    return s


def get_uptime() -> str:
    """Читает /proc/uptime и форматирует в дни/часы/минуты."""
    s = _read_proc(PROC_UPTIME)
    if s.startswith("<"):
        return s
    try:
        sec = float(s.split()[0])
    except (IndexError, ValueError):
        return s
    d = int(sec // 86400)
    h = int((sec % 86400) // 3600)
    m = int((sec % 3600) // 60)
    if d > 0:
        return f"{d} д, {h} ч, {m} мин"
    if h > 0:
        return f"{h} ч, {m} мин"
    return f"{m} мин"


def get_memory_summary() -> str:
    """Парсит /proc/meminfo: MemTotal, MemFree, MemAvailable, Buffers, Cached."""
    text = _read_proc(PROC_MEMINFO)
    if text.startswith("<"):
        return text
    values = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, rest = line.split(":", 1)
        key = key.strip()
        val = rest.strip().split()[0]
        try:
            values[key] = int(val)
        except ValueError:
            continue
    total = values.get("MemTotal", 0)
    available = values.get("MemAvailable", values.get("MemFree", 0))
    if total == 0:
        return "нет данных"
    used = total - available
    total_mb = total // 1024
    used_mb = used // 1024
    avail_mb = available // 1024
    pct = (used * 100) // total if total else 0
    return f"использовано {used_mb} MiB / {total_mb} MiB ({pct}%), свободно {avail_mb} MiB"


def get_cpu_summary() -> str:
    """Количество CPU из /proc/cpuinfo (processor count)."""
    text = _read_proc(PROC_CPUINFO)
    if text.startswith("<"):
        return text
    count = sum(1 for line in text.splitlines() if line.strip().startswith("processor"))
    if count == 0:
        return "нет данных"
    return f"{count} CPU"


def get_disk_summary(path: str = "/") -> str:
    """Использование диска по пути (по умолчанию корень). Использует statvfs."""
    try:
        st = os.statvfs(path)
    except OSError as e:
        return f"ошибка {path}: {e}"
    total = st.f_blocks * st.f_frsize
    free = st.f_bavail * st.f_frsize
    used = total - free
    if total == 0:
        return "нет данных"
    total_gb = total / (1024**3)
    used_gb = used / (1024**3)
    free_gb = free / (1024**3)
    pct = (used * 100) // total if total else 0
    return f"{path}: использовано {used_gb:.1f} GiB / {total_gb:.1f} GiB ({pct}%), свободно {free_gb:.1f} GiB"


def get_hostname() -> str:
    """Имя хоста."""
    try:
        return os.uname().nodename
    except OSError:
        return "?"


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "/"
    print("=== Сводка по системе ===")
    print(f"Хост: {get_hostname()}")
    print(f"Uptime: {get_uptime()}")
    print(f"Load average: {get_load_average()}")
    print(f"CPU: {get_cpu_summary()}")
    print(f"Память: {get_memory_summary()}")
    print(f"Диск: {get_disk_summary(path)}")
    print("=========================")


if __name__ == "__main__":
    main()
