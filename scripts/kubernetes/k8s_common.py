# Общие утилиты для скриптов Kubernetes: вызов kubectl (только чтение).
from __future__ import annotations

import os
import subprocess
import sys
from typing import Optional

KUBECTL = os.environ.get("KUBECTL", "kubectl")
DEFAULT_TIMEOUT = 30


def run(
    *args: str,
    timeout: int = DEFAULT_TIMEOUT,
    kubeconfig: Optional[str] = None,
    context: Optional[str] = None,
) -> tuple[int, str]:
    """Запуск kubectl с аргументами. Возвращает (returncode, stdout)."""
    cmd = [KUBECTL]
    if kubeconfig:
        cmd.extend(["--kubeconfig", kubeconfig])
    if context:
        cmd.extend(["--context", context])
    cmd.extend(args)
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ,
        )
        return (r.returncode, (r.stdout or "").strip())
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return (-1, str(e))


def run_json(*args: str, **kwargs) -> tuple[int, Optional[dict]]:
    """kubectl с -o json; возвращает (code, parsed dict или None). kwargs: timeout, kubeconfig, context."""
    import json
    args_list = list(args)
    if "-o" not in args_list and "--output" not in args_list:
        args_list.extend(["-o", "json"])
    code, out = run(*args_list, **kwargs)
    if code != 0 or not out:
        return (code, None)
    try:
        return (code, json.loads(out))
    except json.JSONDecodeError:
        return (code, None)
