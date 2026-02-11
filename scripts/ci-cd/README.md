# GitLab CI/CD

Примеры пайплайнов и переиспользуемые фрагменты (snippets). Без интеграции с мониторингом.

| Файл | Описание |
|------|----------|
| `example-diagnostics-job.yml` | Job диагностики: system_summary, network_checks, systemd --failed; артефакты report-*.txt |
| `example-backup-scheduled.yml` | Scheduled pipeline: бэкап PostgreSQL (и закомментированный MySQL), ротация 7 дней |
| `example-helm-deploy.yml` | Deploy через Helm: окружения dev/stage/production, свои values по окружению |
| `snippets/` | Фрагменты с комментариями: run python, artifacts, scheduled job, helm upgrade, секреты |

## Подключение примеров в свой проект

В корне репозитория создайте или дополните `.gitlab-ci.yml`:

```yaml
include:
  - local: scripts/ci-cd/example-diagnostics-job.yml
  # - local: scripts/ci-cd/example-backup-scheduled.yml
  # - local: scripts/ci-cd/example-helm-deploy.yml

stages:
  - build
  - test
  - deploy
  - backup
  # .post используется в example-diagnostics-job (опционально)
```

Убедитесь, что в проекте есть папки `scripts/system/`, `scripts/network/`, `scripts/backup/` и т.д. (этот репозиторий).

## Секреты

Задавайте в **Settings -> CI/CD -> Variables** (masked/protected):

- Бэкапы: `PGPASSWORD`, `MYSQL_PWD`, `MONGODB_URI` и т.д.
- Deploy: `KUBECONFIG` (тип File) или токен для доступа к кластеру.

Не храните пароли и ключи в коде.

## Расписание бэкапов

В GitLab: **CI/CD -> Schedules** — создайте расписание (например cron `0 2 * * *` для 02:00 ежедневно). Pipeline с `rules: - if: $CI_PIPELINE_SOURCE == "schedule"` запустит соответствующие jobs.

**Документация:** [../../docs/cicd-gitlab.md](../../docs/cicd-gitlab.md)
