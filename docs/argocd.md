# Argo CD

Скрипты для проверки статуса приложений Argo CD. Только чтение (`argocd app list`).

**Скрипты:** [../scripts/argocd/](../scripts/argocd/)

---

## Скрипты

| Скрипт | Назначение |
|--------|------------|
| `argocd_apps_list.py` | Список всех приложений: имя, статус синхронизации (Synced/OutOfSync), здоровье (Healthy, Degraded, Progressing, Missing и т.д.), namespace назначения. |
| `argocd_apps_problems.py` | Фильтр приложений с проблемами: OutOfSync и/или не Healthy. Опции `--sync-only` (только расхождения), `--health-only` (только ошибки здоровья). |

Учётные данные: переменные **ARGOCD_SERVER** и **ARGOCD_AUTH_TOKEN** или аргументы `--server` и `--auth-token`. Можно предварительно выполнить `argocd login`.

---

## Требования

- **argocd** CLI, доступ к серверу Argo CD (логин или токен).

---

## Примеры

```bash
export ARGOCD_SERVER=https://argocd.example.com
export ARGOCD_AUTH_TOKEN=...

python3 scripts/argocd/argocd_apps_list.py
python3 scripts/argocd/argocd_apps_problems.py
python3 scripts/argocd/argocd_apps_problems.py --sync-only
```
