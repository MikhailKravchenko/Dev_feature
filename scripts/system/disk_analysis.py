#!/usr/bin/env python3
"""
Анализ диска: занятость, поиск больших файлов и каталогов, опционально — каталоги логов.
Только стандартная библиотека Python. Linux/Ubuntu.
Использование:
  python3 disk_analysis.py [каталог] [--top N] [--dirs]
  --top N   вывести топ N больших элементов (по умолчанию 20)
  --dirs    показывать размер каталогов (сумма содержимого; может быть медленно на больших деревьях)
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def format_size(size: int) -> str:
    if size >= 1024**4:
        return f"{size / 1024**4:.1f} TiB"
    if size >= 1024**3:
        return f"{size / 1024**3:.1f} GiB"
    if size >= 1024**2:
        return f"{size / 1024**2:.1f} MiB"
    if size >= 1024:
        return f"{size / 1024:.1f} KiB"
    return f"{size} B"


def get_dir_size(path: Path, follow_symlinks: bool = False) -> int:
    """Рекурсивный размер каталога в байтах."""
    total = 0
    try:
        for entry in path.iterdir():
            try:
                if entry.is_symlink() and not follow_symlinks:
                    continue
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += get_dir_size(entry, follow_symlinks)
            except (OSError, PermissionError):
                pass
    except (OSError, PermissionError):
        pass
    return total


def iter_files_sizes(root: Path, max_depth: int | None = None) -> list[tuple[Path, int]]:
    """Обход файлов с размерами. root — каталог. max_depth — ограничение глубины (None = без ограничения)."""
    result: list[tuple[Path, int]] = []
    root = root.resolve()

    def walk(p: Path, depth: int) -> None:
        if max_depth is not None and depth > max_depth:
            return
        try:
            for entry in p.iterdir():
                try:
                    if entry.is_symlink():
                        continue
                    if entry.is_file():
                        result.append((entry, entry.stat().st_size))
                    elif entry.is_dir():
                        walk(entry, depth + 1)
                except (OSError, PermissionError):
                    pass
        except (OSError, PermissionError):
            pass

    walk(root, 0)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Анализ диска: большие файлы и каталоги")
    parser.add_argument("directory", nargs="?", default="/", help="Каталог для анализа (по умолчанию /)")
    parser.add_argument("--top", type=int, default=20, help="Топ N больших элементов (по умолчанию 20)")
    parser.add_argument("--dirs", action="store_true", help="Учитывать размер каталогов (медленно на больших деревьях)")
    parser.add_argument("--depth", type=int, default=None, help="Макс. глубина обхода (по умолчанию без ограничения)")
    args = parser.parse_args()

    root = Path(args.directory)
    if not root.is_dir():
        print(f"Ошибка: не каталог: {root}", file=sys.stderr)
        sys.exit(1)

    print(f"=== Анализ диска: {root} ===\n")

    # Занятость корня (или указанного каталога)
    try:
        st = os.statvfs(root)
        total = st.f_blocks * st.f_frsize
        free = st.f_bavail * st.f_frsize
        used = total - free
        pct = (used * 100) // total if total else 0
        print(f"Занятость: {format_size(used)} / {format_size(total)} ({pct}%), свободно {format_size(free)}\n")
    except OSError as e:
        print(f"Не удалось получить занятость: {e}\n", file=sys.stderr)

    if args.dirs:
        print("Подсчёт размеров каталогов (может занять время)...")
        dir_sizes: list[tuple[Path, int]] = []
        try:
            for entry in root.iterdir():
                if entry.is_symlink():
                    continue
                if entry.is_dir():
                    size = get_dir_size(entry)
                    dir_sizes.append((entry, size))
        except (OSError, PermissionError) as e:
            print(f"Ошибка обхода: {e}", file=sys.stderr)
        dir_sizes.sort(key=lambda x: x[1], reverse=True)
        print(f"--- Топ {args.top} каталогов по размеру ---")
        for path, size in dir_sizes[: args.top]:
            try:
                rel = path.relative_to(root)
            except ValueError:
                rel = path
            print(f"  {format_size(size):>12}  {rel}")
    else:
        files = iter_files_sizes(root, args.depth)
        files.sort(key=lambda x: x[1], reverse=True)
        print(f"--- Топ {args.top} файлов по размеру ---")
        for path, size in files[: args.top]:
            try:
                rel = path.relative_to(root)
            except ValueError:
                rel = path
            print(f"  {format_size(size):>12}  {rel}")

    print("================================")


if __name__ == "__main__":
    main()
