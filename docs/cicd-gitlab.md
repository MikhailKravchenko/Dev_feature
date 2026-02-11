# GitLab CI/CD

Примеры пайплайнов и jobs для диагностики, бэкапов по расписанию и деплоя через Helm. Без интеграции с мониторингом.

**Примеры и snippets:** [../scripts/ci-cd/](../scripts/ci-cd/)

---

## Примеры пайплайнов

| Файл | Назначение |
|------|------------|
| `example-diagnostics-job.yml` | Job запуска скриптов диагностики (system_summary, network_checks, systemd --failed). Результаты в артефактах (report-*.txt, expire 7 дней). Запуск по schedule, web или при `DIAGNOSTICS_JOB=true`. |
| `example-backup-scheduled.yml` | Scheduled pipeline: job бэкапа PostgreSQL (--dest, --rotate-days 7). Переменные BACKUP_DEST, PG_DATABASE; секреты PGPASSWORD и т.д. в CI/CD Variables. Закомментирован пример для MySQL. |
| `example-helm-deploy.yml` | Deploy через Helm: общий шаблон .helm_deploy и три job (deploy:dev, deploy:stage, deploy:production) с разными environment, namespace и values-file (values-dev/stage/prod.yaml). |

Подключение в `.gitlab-ci.yml`: `include: - local: scripts/ci-cd/example-*.yml`. Настройте переменные и rules под свои ветки и окружения.

---

## Snippets

В каталоге **snippets/** — переиспользуемые фрагменты с пояснениями (формат .md с блоками YAML):

| Snippet | Содержание |
|---------|------------|
| `snippet-run-python.md` | Запуск Python-скрипта в job (image, script, при необходимости before_script и кэш pip). |
| `snippet-artifacts-reports.md` | Сохранение текстовых отчётов в артефакты (paths, expire_in, when: always). |
| `snippet-scheduled-job.md` | Правило rules для запуска только по расписанию ($CI_PIPELINE_SOURCE == "schedule"). |
| `snippet-helm-upgrade.md` | Один job: helm upgrade --install с переменными и опционально --set image.tag. |
| `snippet-secrets-env.md` | Использование CI/CD Variables для паролей и KUBECONFIG (masked, file). |

Копируйте нужные блоки в свой `.gitlab-ci.yml` или используйте как справочник.

---

## Секреты

Учётные данные — только через **CI/CD Variables** (Settings -> CI/CD -> Variables): masked, при необходимости protected или type File. Не храните пароли в коде и не коммитьте их в репозиторий.

---

## Расписание

Для бэкапов по расписанию: **CI/CD -> Schedules** в GitLab, укажите cron (например `0 2 * * *`). Jobs с `rules: - if: $CI_PIPELINE_SOURCE == "schedule"` выполнятся в таких пайплайнах.
