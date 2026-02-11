# Argo CD

Список приложений со статусами Sync/Health и поиск приложений с расхождениями или ошибками. Только чтение (argocd app list).

| Скрипт | Описание |
|--------|----------|
| `argocd_apps_list.py` | Список всех приложений: имя, Sync (Synced/OutOfSync), Health (Healthy/Degraded/...), namespace |
| `argocd_apps_problems.py` | Только приложения OutOfSync или с не Healthy; опции --sync-only, --health-only |

## Переменные окружения

- **ARGOCD_SERVER** — URL сервера Argo CD (например https://argocd.example.com)
- **ARGOCD_AUTH_TOKEN** — токен авторизации (или выполните `argocd login` заранее)

## Примеры

```bash
# Предварительно: argocd login <server> или экспорт ARGOCD_SERVER и ARGOCD_AUTH_TOKEN

# Список всех приложений
python3 argocd_apps_list.py

# Только приложения с проблемами (OutOfSync или не Healthy)
python3 argocd_apps_problems.py

# Только OutOfSync
python3 argocd_apps_problems.py --sync-only

# Только не Healthy (Degraded, Missing, Progressing и т.д.)
python3 argocd_apps_problems.py --health-only

# Указать сервер и токен
python3 argocd_apps_list.py --server https://argocd.example.com --auth-token $TOKEN
```

**Документация:** [../../docs/argocd.md](../../docs/argocd.md)
