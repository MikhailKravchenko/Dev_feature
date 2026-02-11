#!/usr/bin/env python3
"""
Список приложений Argo CD с статусами Sync и Health.
Только чтение (argocd app list). Требуется argocd CLI и доступ к серверу (логин/токен).
Использование:
  python3 argocd_apps_list.py [--server URL] [--auth-token TOKEN]
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
    parser = argparse.ArgumentParser(description="Список приложений Argo CD (Sync/Health)")
    parser.add_argument("--server", "-s", default=os.environ.get("ARGOCD_SERVER"), help="URL сервера Argo CD")
    parser.add_argument("--auth-token", default=os.environ.get("ARGOCD_AUTH_TOKEN"), help="Токен авторизации")
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
        # Fallback: вывести как есть (если вернули не JSON)
        print(out)
        return 0

    # Формат ответа: может быть список или объект с ключом items
    items = data if isinstance(data, list) else data.get("items", data) if isinstance(data, dict) else []
    if not isinstance(items, list):
        items = [data]

    if not items:
        print("Приложений не найдено.")
        return 0

    print("=== Приложения Argo CD (Sync / Health) ===\n")
    print(f"  {'NAME':<40} {'SYNC':<12} {'HEALTH':<12} {'NAMESPACE':<24}")
    print("  " + "-" * 90)
    for app in items:
        if isinstance(app, dict):
            name = app.get("metadata", {}).get("name") or app.get("name", "?")
            ns = app.get("spec", {}).get("destination", {}).get("namespace") or app.get("metadata", {}).get("namespace", "")
            sync = (app.get("status", {}).get("sync", {}).get("status") or "Unknown")
            health = (app.get("status", {}).get("health", {}).get("status") or "Unknown")
            print(f"  {name:<40} {sync:<12} {health:<12} {str(ns):<24}")
        else:
            print(f"  {app}")
    print("\n================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
