# Snippet: запуск Python-скрипта в job

Использование образа с Python и запуск скрипта из репозитория.

```yaml
job-name:
  image: python:3.11-slim
  script:
    - python3 scripts/system/system_summary.py
  # Если нужны системные утилиты (ss, systemctl):
  # before_script:
  #   - apt-get update -qq && apt-get install -y -qq iproute2 2>/dev/null || true
```

Вариант с кэшем pip (если есть requirements.txt):

```yaml
job-name:
  image: python:3.11-slim
  cache:
    key: pip
    paths: [.cache/pip]
  before_script:
    - pip install --cache-dir .cache/pip -r requirements.txt 2>/dev/null || true
  script:
    - python3 path/to/script.py
```
