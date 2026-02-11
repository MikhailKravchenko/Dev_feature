#!/usr/bin/env python3
"""
Набор read-only проверок: только kubectl get/list, без изменений ресурсов.
Удобно для ролей с ограниченными правами (get, list). Запускает базовые проверки и выводит результат.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from k8s_common import run


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only проверки K8s (только get/list)")
    parser.add_argument("--context", "-c", help="kubectl context")
    parser.add_argument("--kubeconfig", help="Путь к kubeconfig")
    args = parser.parse_args()
    ctx, kcfg = args.context, args.kubeconfig

    def k(*a):
        return run(*a, context=ctx, kubeconfig=kcfg)

    print("=== Read-only проверки (get/list) ===\n")
    checks = [
        ("get nodes", ["get", "nodes", "-o", "wide"]),
        ("get ns", ["get", "ns"]),
        ("get pods -A (кратко)", ["get", "pods", "-A", "--no-headers"]),
    ]
    for label, cmd in checks:
        print(f"--- {label} ---")
        code, out = k(*cmd)
        if code != 0:
            print(f"  Ошибка (код {code}): {out or 'нет вывода'}")
        elif out:
            lines = out.strip().splitlines()
            for ln in lines[:20]:
                print(f"  {ln}")
            if len(lines) > 20:
                print(f"  ... ({len(lines) - 20} ещё)")
        else:
            print("  (пусто)")
        print()
    print("================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
