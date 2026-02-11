#!/usr/bin/env python3
"""
Базовые проверки безопасности: открытые порты, права на ключевые файлы.
Только чтение и анализ, без изменений. Linux/Ubuntu.
Использование:
  python3 security_checks.py [--ports] [--files] [--all]
  --ports   показать слушающие порты (ss -tuln)
  --files   проверить права на ключевые файлы (/etc/shadow, ssh keys, cron)
  --all     все проверки (по умолчанию при отсутствии флагов)
"""
from __future__ import annotations

import argparse
import os
import stat
import subprocess
import sys
from pathlib import Path

# Файлы, которые желательно иметь с ограниченными правами
# (путь, рекомендуемые права в восьмеричном виде, описание)
CRITICAL_FILES = [
    ("/etc/shadow", 0o600, "должен быть 600 или 640"),
    ("/etc/gshadow", 0o600, "должен быть 600 или 640"),
    ("/etc/passwd", 0o644, "обычно 644"),
    ("/etc/group", 0o644, "обычно 644"),
    ("/etc/ssh/sshd_config", 0o600, "рекомендуется 600"),
]

# Каталоги для проверки прав на ключи SSH (файлы ключей должны быть 600)
SSH_KEY_DIRS = [
    "/root/.ssh",
    "/etc/ssh",
]


def run_ss_ports() -> str:
    """Слушающие порты (ss -tuln)."""
    try:
        r = subprocess.run(
            ["ss", "-tuln"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return r.stdout.strip() if r.returncode == 0 else ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def check_file_perms(path: str, expected_mode: int, desc: str) -> list[str]:
    """Проверка прав на файл. Возвращает список строк-предупреждений (пусто = всё ок)."""
    lines = []
    try:
        st = os.stat(path)
        mode = st.st_mode & 0o777
        if path in ("/etc/passwd", "/etc/group"):
            # 644 типично
            if mode != 0o644:
                if mode & 0o002:  # other writable
                    lines.append(f"  {path}: режим {oct(mode)} — доступ на запись для others!")
                elif mode > 0o644:
                    lines.append(f"  {path}: режим {oct(mode)} (ожидается 644), {desc}")
        else:
            # Более строгие файлы: не должны быть доступны на запись для group/other
            if (mode & 0o022) != 0:
                lines.append(f"  {path}: режим {oct(mode)} — запись для group/other нежелательна. {desc}")
            elif mode != expected_mode and (expected_mode & 0o400) and not (mode & 0o400):
                lines.append(f"  {path}: режим {oct(mode)} (ожидается {oct(expected_mode)}). {desc}")
    except FileNotFoundError:
        lines.append(f"  {path}: файл не найден (пропуск)")
    except OSError as e:
        lines.append(f"  {path}: ошибка доступа — {e}")
    return lines


def check_ssh_key_perms() -> list[str]:
    """Проверка прав на файлы в .ssh: ключи должны быть 600, каталог 700."""
    lines = []
    for dir_path in SSH_KEY_DIRS:
        d = Path(dir_path)
        if not d.is_dir():
            continue
        try:
            st = d.stat()
            mode = st.st_mode & 0o777
            if mode != 0o700:
                lines.append(f"  {dir_path}: режим каталога {oct(mode)} (рекомендуется 700)")
        except OSError:
            continue
        for f in d.iterdir():
            if f.is_file() and (f.suffix in (".pem", "") or "key" in f.name.lower() or f.name.startswith("id_")):
                try:
                    st = f.stat()
                    mode = st.st_mode & 0o777
                    if (mode & 0o077) != 0:
                        lines.append(f"  {f}: режим {oct(mode)} (рекомендуется 600 для ключей)")
                except OSError:
                    pass
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Базовые проверки безопасности (только чтение)")
    parser.add_argument("--ports", action="store_true", help="Показать слушающие порты")
    parser.add_argument("--files", action="store_true", help="Проверить права на ключевые файлы")
    parser.add_argument("--all", action="store_true", help="Все проверки")
    args = parser.parse_args()

    if not any([args.ports, args.files, args.all]):
        args.all = True

    issues = []

    if args.ports or args.all:
        print("=== Слушающие порты (ss -tuln) ===")
        out = run_ss_ports()
        if out:
            print(out)
        else:
            print("(ss недоступен или пустой вывод)")
        print()

    if args.files or args.all:
        print("=== Права на ключевые файлы ===")
        for path, expected, desc in CRITICAL_FILES:
            for line in check_file_perms(path, expected, desc):
                print(line)
                issues.append(line)
        for line in check_ssh_key_perms():
            print(line)
            issues.append(line)
        if not issues:
            print("  Замечаний по указанным файлам нет.")
        print()

    print("================================")
    if issues:
        sys.exit(1)  # Есть замечания — ненулевой код выхода для скриптов/CI
    sys.exit(0)


if __name__ == "__main__":
    main()
