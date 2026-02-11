#!/usr/bin/env python3
"""
Сводка по ресурсам: requests/limits по подам (из манифеста), опционально kubectl top.
Только чтение. Поддержка --context, --kubeconfig, --namespace.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from k8s_common import run, run_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Сводка по ресурсам K8s: requests/limits, top")
    parser.add_argument("--context", "-c", help="kubectl context")
    parser.add_argument("--kubeconfig", help="Путь к kubeconfig")
    parser.add_argument("--namespace", "-n", help="Ограничить namespace")
    parser.add_argument("--top", action="store_true", help="Вызвать kubectl top nodes и top pods (нужен metrics-server)")
    args = parser.parse_args()
    ctx, kcfg = args.context, args.kubeconfig

    def k(*a):
        return run(*a, context=ctx, kubeconfig=kcfg)

    def k_json(*a):
        return run_json(*a, context=ctx, kubeconfig=kcfg)

    cmd = ["get", "pods", "-A", "-o", "json"]
    if args.namespace:
        cmd = ["get", "pods", "-n", args.namespace, "-o", "json"]
    code, data = k_json(*cmd)
    if code != 0 or not data or "items" not in data:
        print("Не удалось получить список подов.")
        return 1

    # Агрегация по namespace: сумма requests/limits
    ns_totals = {}
    for item in data.get("items", []):
        ns = item.get("metadata", {}).get("namespace", "")
        spec = item.get("spec", {})
        for c in spec.get("containers", []):
            res = c.get("resources", {}) or {}
            req = res.get("requests", {}) or {}
            lim = res.get("limits", {}) or {}
            if ns not in ns_totals:
                ns_totals[ns] = {"cpu_req": 0.0, "mem_req": 0, "cpu_lim": 0.0, "mem_lim": 0}
            # Упрощённый парсинг: cpu в millicore или number, memory в Ki/Mi/Gi
            def parse_cpu(s):
                if not s:
                    return 0.0
                s = str(s).strip()
                if s.endswith("m"):
                    return int(s[:-1]) / 1000.0
                try:
                    return float(s)
                except ValueError:
                    return 0.0
            def parse_mem(s):
                if not s:
                    return 0
                s = str(s).strip()
                mult = 1
                if s.endswith("Ki"):
                    mult = 1024
                    s = s[:-2]
                elif s.endswith("Mi"):
                    mult = 1024 * 1024
                    s = s[:-2]
                elif s.endswith("Gi"):
                    mult = 1024 ** 3
                    s = s[:-2]
                try:
                    return int(float(s) * mult)
                except ValueError:
                    return 0
            ns_totals[ns]["cpu_req"] += parse_cpu(req.get("cpu"))
            ns_totals[ns]["mem_req"] += parse_mem(req.get("memory"))
            ns_totals[ns]["cpu_lim"] += parse_cpu(lim.get("cpu"))
            ns_totals[ns]["mem_lim"] += parse_mem(lim.get("memory"))

    print("=== Requests/Limits по namespace (из манифестов подов) ===\n")
    print(f"  {'Namespace':<30} {'CPU req':>12} {'Mem req':>12} {'CPU lim':>12} {'Mem lim':>12}")
    print("  " + "-" * 78)
    for ns in sorted(ns_totals.keys()):
        t = ns_totals[ns]
        mem_req_mib = t["mem_req"] / (1024 * 1024)
        mem_lim_mib = t["mem_lim"] / (1024 * 1024) if t["mem_lim"] else 0
        print(f"  {ns:<30} {t['cpu_req']:>10.2f}   {mem_req_mib:>8.1f}Mi {t['cpu_lim']:>10.2f}   {mem_lim_mib:>8.1f}Mi")
    print()

    if args.top:
        print("=== kubectl top nodes ===\n")
        code, out = k("top", "nodes")
        if code == 0:
            print(out)
        else:
            print(out or " (требуется metrics-server)")
        print("\n=== kubectl top pods -A (первые 40) ===\n")
        code, out = k("top", "pods", "-A")
        if code == 0 and out:
            lines = out.strip().splitlines()
            for line in lines[:41]:
                print(line)
            if len(lines) > 41:
                print("  ...")
        else:
            print(out or " (требуется metrics-server)")
    print("\n================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
