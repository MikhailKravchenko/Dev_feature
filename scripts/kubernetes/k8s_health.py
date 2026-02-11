#!/usr/bin/env python3
"""
Здоровье кластера Kubernetes: ноды, поды (по namespace), события, поды с рестартами.
Только чтение (kubectl get). Поддержка --context и --kubeconfig.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from k8s_common import run, run_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Здоровье кластера K8s: ноды, поды, события, рестарты")
    parser.add_argument("--context", "-c", help="kubectl context")
    parser.add_argument("--kubeconfig", help="Путь к kubeconfig")
    parser.add_argument("--namespace", "-n", help="Ограничить namespace (по умолчанию все)")
    parser.add_argument("--events", action="store_true", default=True, help="Показать события (по умолчанию да)")
    parser.add_argument("--no-events", action="store_false", dest="events", help="Не показывать события")
    args = parser.parse_args()
    ctx, kcfg = args.context, args.kubeconfig

    def k(*a):
        return run(*a, context=ctx, kubeconfig=kcfg)

    def k_json(*a):
        return run_json(*a, context=ctx, kubeconfig=kcfg)

    print("=== Ноды ===\n")
    code, out = k("get", "nodes", "-o", "wide")
    if code != 0:
        print(out or "Ошибка kubectl get nodes")
        return 1
    print(out)
    print()

    print("=== Поды (статус) ===\n")
    cmd = ["get", "pods", "-A", "-o", "wide"]
    if args.namespace:
        cmd = ["get", "pods", "-n", args.namespace, "-o", "wide"]
    code, out = k(*cmd)
    if code == 0:
        print(out)
    else:
        print(out or "Ошибка get pods")
    print()

    # Поды с рестартами > 0
    code, data = k_json("get", "pods", "-A")
    if code == 0 and data and "items" in data:
        restarts = []
        for item in data.get("items", []):
            status = item.get("status", {})
            ns = item.get("metadata", {}).get("namespace", "")
            name = item.get("metadata", {}).get("name", "")
            for cs in status.get("containerStatuses") or []:
                r = cs.get("restartCount", 0)
                if r > 0:
                    restarts.append((ns, name, r))
        if restarts:
            print("=== Поды с рестартами (> 0) ===\n")
            for ns, name, r in sorted(restarts, key=lambda x: -x[2])[:30]:
                print(f"  {ns:20} {name:50} restarts={r}")
            if len(restarts) > 30:
                print(f"  ... и ещё {len(restarts) - 30}")
            print()
        else:
            print("=== Поды с рестартами: нет ===\n")
    else:
        print("=== Рестарты: не удалось получить данные ===\n")

    if args.events:
        print("=== События (последние) ===\n")
        code, out = k("get", "events", "-A", "--sort-by=.lastTimestamp", "-o", "wide")
        if code == 0 and out:
            lines = out.strip().splitlines()
            if len(lines) > 1:
                print("\n".join(lines[-25:]))  # последние 25
            else:
                print(out)
        else:
            print(out or "(нет событий или ошибка)")
        print()

    print("================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
