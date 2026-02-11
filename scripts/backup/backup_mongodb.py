#!/usr/bin/env python3
"""
Бэкап MongoDB: mongodump. В каталог с датой в имени (архив BSON + metadata).
Переменные окружения: MONGODB_URI или --uri. Опционально --gzip для сжатия (mongodump --gzip).
Использование:
  python3 backup_mongodb.py --dest /backup/mongo [--uri URI] [--gzip] [--rotate-days N]
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backup_common import dated_path, log, run


def main() -> int:
    parser = argparse.ArgumentParser(description="Бэкап MongoDB (mongodump)")
    parser.add_argument("--dest", required=True, help="Каталог для сохранения бэкапов")
    parser.add_argument("--uri", default=os.environ.get("MONGODB_URI"), help="MongoDB URI (или MONGODB_URI)")
    parser.add_argument("--gzip", action="store_true", help="Сжатие дампов (mongodump --gzip)")
    parser.add_argument("--rotate-days", type=int, default=0, help="Удалить бэкапы старше N дней")
    parser.add_argument("--mongodump", default="mongodump", help="Путь к mongodump")
    args = parser.parse_args()

    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    out_dir = dated_path(dest, "mongo", "")
    out_dir.mkdir(parents=True, exist_ok=True)

    log(f"Бэкап MongoDB в {out_dir}")
    cmd = [args.mongodump, "--out", str(out_dir)]
    if args.uri:
        cmd.extend(["--uri", args.uri])
    if args.gzip:
        cmd.append("--gzip")

    code = run(cmd, log_prefix="[mongodump] ")
    if code != 0:
        return code

    if args.rotate_days > 0:
        cutoff = time.time() - args.rotate_days * 86400
        for d in dest.iterdir():
            if d.is_dir() and d.name.startswith("mongo_") and d.stat().st_mtime < cutoff:
                try:
                    log(f"Ротация: удаление {d}")
                    shutil.rmtree(d)
                except OSError as e:
                    log(f"Ошибка удаления {d}: {e}")

    log("Готово.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
