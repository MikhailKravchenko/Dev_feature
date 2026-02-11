# Snippet: job только по расписанию

Запуск job только когда pipeline вызван по schedule (CI/CD -> Schedules).

```yaml
backup-job:
  stage: backup
  script:
    - python3 scripts/backup/backup_postgres.py --dest /backup --rotate-days 7
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
```

Дополнительно разрешить ручной запуск из UI:

```yaml
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
    - if: $CI_PIPELINE_SOURCE == "web"
```

Проверка переменной (например кастомный флаг):

```yaml
  rules:
    - if: $RUN_BACKUP == "true"
```
