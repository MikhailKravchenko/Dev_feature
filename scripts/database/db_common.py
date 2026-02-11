# Общие утилиты для траблшутинга БД: подсветка выхода за рамки, вывод в консоль.
from __future__ import annotations

import os
import subprocess
import sys

# Подсветка: если вывод в TTY — используем ANSI-коды, иначе — префиксы [WARN]/[OK]
USE_COLOR = hasattr(sys.stdout, "isatty") and sys.stdout.isatty() and os.environ.get("NO_COLOR", "") == ""

RED = "\033[91m" if USE_COLOR else ""
GREEN = "\033[92m" if USE_COLOR else ""
YELLOW = "\033[93m" if USE_COLOR else ""
BOLD = "\033[1m" if USE_COLOR else ""
RESET = "\033[0m" if USE_COLOR else ""


def ok(msg: str) -> str:
    return f"{GREEN}[OK]{RESET} {msg}" if USE_COLOR else f"[OK] {msg}"


def warn(msg: str) -> str:
    return f"{RED}[WARN]{RESET} {msg}" if USE_COLOR else f"[WARN] {msg}"


def section(title: str) -> None:
    print(f"\n{BOLD}=== {title} ==={RESET}\n", file=sys.stderr if not USE_COLOR else sys.stderr)


def line(name: str, value: str | int | float, is_warn: bool = False) -> None:
    s = f"  {name}: {value}"
    print(warn(s) if is_warn else s)


def line_with_threshold(
    name: str,
    value: int | float,
    unit: str,
    *,
    warn_above: float | None = None,
    warn_below: float | None = None,
    warn_if_none: bool = False,
) -> None:
    if value is None and warn_if_none:
        line(name, f"? {unit}", is_warn=True)
        return
    if value is None:
        line(name, f"? {unit}")
        return
    is_warn = False
    if warn_above is not None and value > warn_above:
        is_warn = True
    if warn_below is not None and value < warn_below:
        is_warn = True
    line(name, f"{value} {unit}", is_warn=is_warn)


def run_cmd(cmd: list[str], timeout: int = 15, env: dict | None = None) -> tuple[int, str]:
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, **(env or {})},
        )
        return (r.returncode, (r.stdout or "").strip())
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return (-1, str(e))
