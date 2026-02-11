# Snippet: артефакты — текстовые отчёты

Сохранение файлов-отчётов для скачивания из пайплайна.

```yaml
report-job:
  script:
    - python3 scripts/system/system_summary.py 2>&1 | tee report-system.txt
    - python3 scripts/network/network_checks.py --ports 2>&1 | tee report-ports.txt
  artifacts:
    when: always   # сохранять даже при падении job
    paths:
      - report-*.txt
    expire_in: 7 days
```

Для архивов (например бэкапов):

```yaml
  artifacts:
    paths: [backups/]
    expire_in: 1 day
```
