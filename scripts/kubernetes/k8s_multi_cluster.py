#!/usr/bin/env python3
"""
Мульти-кластер: список контекстов, выполнение проверки для каждого контекста (или выбранных).
Только чтение. Использование:
  python3 k8s_multi_cluster.py                    # список контекстов и текущий
  python3 k8s_multi_cluster.py --run-health      # запустить k8s_health для каждого контекста
  python3 k8s_multi_cluster.py --contexts ctx1,ctx2 --run-health
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from k8s_common import run


def main() -> int:
    parser = argparse.ArgumentParser(description="Мульти-кластер: контексты, проверка по каждому")
    parser.add_argument("--kubeconfig", help="Путь к kubeconfig")
    parser.add_argument("--contexts", help="Список контекстов через запятую (по умолчанию все)")
    parser.add_argument("--run-health", action="store_true", help="Запустить k8s_health.py для каждого контекста")
    args = parser.parse_args()

    cmd = ["kubectl", "config", "get-contexts", "-o", "name"]
    if args.kubeconfig:
        cmd.extend(["--kubeconfig", args.kubeconfig])
    code, out = run(*cmd[1:], kubeconfig=args.kubeconfig)
    if code != 0:
        # fallback: run directly
        import os
        env = os.environ.copy()
        full_cmd = ["kubectl", "config", "get-contexts", "-o", "name"]
        if args.kubeconfig:
            full_cmd = ["kubectl", "--kubeconfig", args.kubeconfig, "config", "get-contexts", "-o", "name"]
        r = subprocess.run(full_cmd, capture_output=True, text=True, timeout=15, env=env)
        out = (r.stdout or "").strip()
        code = r.returncode
    if code != 0 or not out:
        print("Не удалось получить список контекстов.")
        return 1

    contexts = [c.strip() for c in out.splitlines() if c.strip()]
    if args.contexts:
        wanted = [c.strip() for c in args.contexts.split(",") if c.strip()]
        contexts = [c for c in contexts if c in wanted]
        if not contexts:
            print("Ни один из указанных контекстов не найден.")
            return 1

    print("=== Контексты (текущий отмечен * в kubectl config current-context) ===\n")
    for c in contexts:
        print(f"  {c}")
    print()

    if args.run_health:
        script = Path(__file__).resolve().parent / "k8s_health.py"
        if not script.exists():
            print("k8s_health.py не найден.")
            return 1
        for ctx in contexts:
            print(f"\n{'='*60}\n  Контекст: {ctx}\n{'='*60}\n")
            run_cmd = [sys.executable, str(script), "--context", ctx]
            if args.kubeconfig:
                run_cmd.extend(["--kubeconfig", args.kubeconfig])
            subprocess.run(run_cmd, timeout=120)
    else:
        print("Для запуска проверки по каждому контексту используйте --run-health")

    print("\n================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
