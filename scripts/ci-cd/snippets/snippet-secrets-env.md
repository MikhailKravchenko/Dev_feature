# Snippet: секреты через CI/CD Variables

Учётные данные и ключи задаются в GitLab: Settings -> CI/CD -> Variables. Не храните пароли в коде.

- **Mask variable** — значение скрыто в логах.
- **Protected** — только в пайплайнах защищённых веток.
- **File** — значение записывается во временный файл, переменная содержит путь.

Пример использования в job:

```yaml
backup-postgres:
  script:
    - python3 scripts/backup/backup_postgres.py --dest /backup -d mydb --rotate-days 7
  # PGPASSWORD, PGHOST, PGUSER заданы в CI/CD Variables (masked)
```

Переменная типа File (например KUBECONFIG):

```yaml
deploy:
  variables:
    KUBECONFIG: $KUBECONFIG_FILE   # в Variables создан ключ KUBECONFIG_FILE, тип File
  script:
    - helm upgrade --install ...
```

Список типичных переменных для скриптов из этого репозитория:

| Переменная   | Где используется | Рекомендация  |
|-------------|------------------|---------------|
| PGPASSWORD  | backup/restore PG | Masked       |
| MYSQL_PWD   | backup/restore MySQL | Masked   |
| MONGODB_URI | backup/restore MongoDB | Masked  |
| ARGOCD_AUTH_TOKEN | argocd apps | Masked      |
| KUBECONFIG  | helm, k8s        | File или Masked |
