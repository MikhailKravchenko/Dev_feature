#!/usr/bin/env python3
"""
Поиск подов с образами без тега или с тегом latest.
Только чтение (kubectl get pods -o json). Поддержка --context, --kubeconfig, --namespace.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from k8s_common import run_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Поды с образами :latest или без тега")
    parser.add_argument("--context", "-c", help="kubectl context")
    parser.add_argument("--kubeconfig", help="Путь к kubeconfig")
    parser.add_argument("--namespace", "-n", help="Ограничить namespace")
    args = parser.parse_args()

    cmd = ["get", "pods", "-A", "-o", "json"]
    if args.namespace:
        cmd = ["get", "pods", "-n", args.namespace, "-o", "json"]
    code, data = run_json(*cmd, context=args.context, kubeconfig=args.kubeconfig)
    if code != 0 or not data or "items" not in data:
        print("Не удалось получить список подов.")
        return 1

    found = []
    for item in data.get("items", []):
        ns = item.get("metadata", {}).get("namespace", "")
        name = item.get("metadata", {}).get("name", "")
        for c in item.get("spec", {}).get("containers", []) + item.get("spec", {}).get("initContainers", []):
            image = c.get("image", "")
            if not image:
                continue
            # Образ без тега (только имя:версия или репо/имя) или с :latest
            if image.endswith(":latest") or ":latest-" in image:
                found.append((ns, name, image, "latest"))
            elif ":" not in image.split("/")[-1]:
                # последний компонент (после /) без ":" — нет тега
                last = image.split("/")[-1]
                if last and ":" not in last:
                    found.append((ns, name, image, "no tag"))
    if not found:
        print("Подов с образами :latest или без тега не найдено.")
        return 0
    print("=== Поды с образами :latest или без тега ===\n")
    print(f"  {'Namespace':<24} {'Pod':<50} {'Причина':<8} Image")
    print("  " + "-" * 100)
    for ns, pod, image, reason in found[:60]:
        print(f"  {ns:<24} {pod:<50} {reason:<8} {image}")
    if len(found) > 60:
        print(f"  ... и ещё {len(found) - 60}")
    print("\n================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
