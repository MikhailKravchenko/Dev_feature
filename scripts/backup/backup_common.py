# Общие утилиты для скриптов бэкапа: пути с датой, ротация, вызов команд, логирование в stderr.
from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def dated_path(directory: str | Path, prefix: str, suffix: str) -> Path:
    """Путь к файлу бэкапа: directory/prefix_YYYY-MM-DD_HH-MM suffix."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return directory / f"{prefix}_{stamp}{suffix}"


def run(cmd: list[str], env: dict | None = None, log_prefix: str = "") -> int:
    """Запуск команды. Логирует команду в stderr. Возвращает код выхода."""
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    msg = f"{log_prefix}Выполняется: {' '.join(cmd)}"
    print(msg, file=sys.stderr)
    try:
        r = subprocess.run(cmd, env=full_env, timeout=3600)
        return r.returncode
    except subprocess.TimeoutExpired:
        print("Ошибка: таймаут команды", file=sys.stderr)
        return -1
    except FileNotFoundError as e:
        print(f"Ошибка: команда не найдена — {e}", file=sys.stderr)
        return -1
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return -1


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def rotate_by_days(directory: Path, prefix: str, days: int) -> None:
    """Удалить файлы в directory с именем, начинающимся на prefix, старше days дней."""
    if days <= 0:
        return
    now = time.time()
    cutoff = now - days * 86400
    directory = Path(directory)
    if not directory.is_dir():
        return
    for f in directory.iterdir():
        if f.is_file() and f.name.startswith(prefix):
            try:
                if f.stat().st_mtime < cutoff:
                    log(f"Ротация: удаление {f}")
                    f.unlink()
            except OSError as e:
                log(f"Ошибка удаления {f}: {e}")


def rotate_keep_n(directory: Path, prefix: str, keep: int) -> None:
    """Оставить только последние keep файлов (по mtime) с именем, начинающимся на prefix; остальные удалить."""
    if keep <= 0:
        return
    directory = Path(directory)
    if not directory.is_dir():
        return
    candidates = []
    for f in directory.iterdir():
        if f.is_file() and f.name.startswith(prefix):
            try:
                candidates.append((f.stat().st_mtime, f))
            except OSError:
                pass
    candidates.sort(key=lambda x: x[0], reverse=True)
    for _, f in candidates[keep:]:
        try:
            log(f"Ротация: удаление {f}")
            f.unlink()
        except OSError as e:
            log(f"Ошибка удаления {f}: {e}")
