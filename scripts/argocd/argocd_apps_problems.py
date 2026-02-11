#!/usr/bin/env python3
"""
Поиск приложений Argo CD с расхождениями (OutOfSync) или с ошибками по здоровью (не Healthy).
Только чтение. Требуется argocd CLI и доступ к серверу.
Использование:
  python3 argocd_apps_problems.py [--server URL] [--auth-token TOKEN] [--sync-only] [--health-only]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys


def run_argocd(*args: str, server: str | None = None, auth_token: str | None = None) -> tuple[int, str]:
    cmd = ["argocd", "app", "list"]
    if server:
        cmd.extend(["--server", server])
    if auth_token:
        cmd.extend(["--auth-token", auth_token])
    cmd.extend(args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=os.environ)
        return (r.returncode, (r.stdout or "").strip())
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return (-1, str(e))


def main() -> int:
    parser = argparse.ArgumentParser(description="Argo CD: приложения OutOfSync или с ошибками здоровья")
    parser.add_argument("--server", "-s", default=os.environ.get("ARGOCD_SERVER"), help="URL сервера Argo CD")
    parser.add_argument("--auth-token", default=os.environ.get("ARGOCD_AUTH_TOKEN"), help="Токен авторизации")
    parser.add_argument("--sync-only", action="store_true", help="Показать только OutOfSync")
    parser.add_argument("--health-only", action="store_true", help="Показать только не Healthy (Degraded, Missing, Progressing и т.д.)")
    args = parser.parse_args()

    code, out = run_argocd("-o", "json", server=args.server, auth_token=args.auth_token)
    if code != 0:
        print(f"Ошибка argocd: {out or 'нет вывода'}", file=sys.stderr)
        return 1

    if not out:
        print("Приложений не найдено.")
        return 0

    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        print("Не удалось разобрать ответ argocd.", file=sys.stderr)
        return 1

    items = data if isinstance(data, list) else data.get("items", data) if isinstance(data, dict) else []
    if not isinstance(items, list):
        items = [data]

    problems = []
    for app in items:
        if not isinstance(app, dict):
            continue
        name = app.get("metadata", {}).get("name") or app.get("name", "?")
        ns = app.get("spec", {}).get("destination", {}).get("namespace") or ""
        sync = (app.get("status", {}).get("sync", {}).get("status") or "Unknown")
        health = (app.get("status", {}).get("health", {}).get("status") or "Unknown")
        out_of_sync = sync == "OutOfSync"
        unhealthy = health and health != "Healthy" and health != "Suspended"
        if args.sync_only and not out_of_sync:
            continue
        if args.health_only and not unhealthy:
            continue
        if not args.sync_only and not args.health_only:
            if not (out_of_sync or unhealthy):
                continue
        problems.append((name, ns, sync, health))

    if not problems:
        print("Приложений с расхождениями или ошибками здоровья не найдено.")
        return 0

    print("=== Приложения с проблемами (OutOfSync или не Healthy) ===\n")
    print(f"  {'NAME':<40} {'SYNC':<12} {'HEALTH':<12} {'NAMESPACE':<20}")
    print("  " + "-" * 86)
    for name, ns, sync, health in problems:
        print(f"  {name:<40} {sync:<12} {health:<12} {str(ns):<20}")
    print(f"\n  Всего: {len(problems)}")
    print("\n================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
