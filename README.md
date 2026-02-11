# DevOps-инженер: скрипты и справочник

Личный репозиторий скриптов для диагностики, траблшутинга и автоматизации на Ubuntu.  
Предпочтение: **Python** (стандартная библиотека); **Bash** — где уместнее (обёртки, cron, вызовы kubectl/helm).

---

## Структура репозитория

```
├── docs/                    # Документация по темам
├── scripts/
│   ├── system/              # Диагностика Linux (ресурсы, диск, логи, сервисы)
│   ├── network/             # Сетевые проверки
│   ├── backup/              # Бэкапы СУБД (все поддерживаемые)
│   ├── database/            # Troubleshooting СУБД: определение, состояние, параметры, пороги
│   ├── restore/             # Сценарии восстановления из бэкапов
│   ├── kubernetes/          # K8s: здоровье кластера, ресурсы, read-only скрипты
│   ├── argocd/              # Argo CD: статус приложений, расхождения
│   ├── helm/                # Helm: lint, diff, шаблоны
│   └── ci-cd/               # Примеры GitLab CI/CD (pipelines, jobs)
└── README.md
```

---

## План наполнения

### 1. Диагностика и траблшутинг Linux (Ubuntu) ✅

| # | Скрипт / раздел | Описание | Язык |
|---|-----------------|----------|------|
| 1.1 | Сводка по системе | CPU, RAM, диск, load, uptime | Python |
| 1.2 | Анализ диска | Занятость, большие файлы/каталоги, рост логов | Python |
| 1.3 | Сетевые проверки | Порты, соединения, DNS, базовые HTTP-проверки | Python/Bash |
| 1.4 | Анализ логов | Поиск ошибок, частых сообщений, ротация | Python |
| 1.5 | Проверка сервисов (systemd) | Статус, перезапуски, зависимости | Python/Bash |
| 1.6 | Базовые проверки безопасности | Открытые порты, подозрительные процессы, права на ключевые файлы | Python |

**Документ:** [docs/diagnostics.md](docs/diagnostics.md)

---

### 2. Бэкапы баз данных ✅

Поддержка всех основных СУБД + сценарии восстановления и проверки целостности.

| # | Скрипт / раздел | Описание | Язык |
|---|-----------------|----------|------|
| 2.1 | PostgreSQL | dump (full/schema), сжатие, ротация, лог | Python/Bash |
| 2.2 | MySQL / MariaDB | mysqldump, сжатие, ротация | Python/Bash |
| 2.3 | MongoDB | mongodump, опции, ротация | Python/Bash |
| 2.4 | Redis | RDB snapshot / BGSAVE, копирование файла | Python/Bash |
| 2.5 | Ротация и политика хранения | Удаление старых бэкапов по возрасту/количеству | Python |
| 2.6 | Проверка бэкапов | Проверка целостности (например, pg_restore --list для PG) | Python/Bash |

**Документ:** [docs/backups.md](docs/backups.md)

---

### 2.1 Troubleshooting СУБД ✅

Определить, какие БД запущены на сервере, и вывести состояние и параметры с подсветкой при выходе за пороги.

| Скрипт | Описание |
|--------|----------|
| `detect_databases.py` | Определение запущенных СУБД по портам (и systemd) |
| `troubleshoot_all.py` | Единая точка входа: все обнаруженные СУБД |
| `troubleshoot_postgres.py` | PostgreSQL: соединения, память, репликация, долгие запросы |
| `troubleshoot_mysql.py` | MySQL/MariaDB: соединения, InnoDB, репликация |
| `troubleshoot_mongodb.py` | MongoDB: соединения, память, replica set |
| `troubleshoot_redis.py` | Redis: клиенты, память, персистентность, репликация |

**Папка:** [scripts/database/](scripts/database/) · **Документ:** [docs/database-troubleshooting.md](docs/database-troubleshooting.md)

---

### 3. Восстановление из бэкапов

| # | Скрипт / раздел | Описание | Язык |
|---|-----------------|----------|------|
| 3.1 | PostgreSQL | restore из custom/directory format, проверка | Python/Bash |
| 3.2 | MySQL / MariaDB | Восстановление из dump | Python/Bash |
| 3.3 | MongoDB | mongorestore | Python/Bash |
| 3.4 | Redis | Подмена RDB, перезапуск | Bash |

**Документ:** [docs/restore.md](docs/restore.md)

---

### 4. Kubernetes (несколько кластеров)

Скрипты в том числе с **ограниченным доступом** (read-only).

| # | Скрипт / раздел | Описание | Язык |
|---|-----------------|----------|------|
| 4.1 | Здоровье кластера | Ноды, поды, события, недавние рестарты | Python/Bash |
| 4.2 | Сводка по ресурсам | Requests/limits, использование по namespace | Python |
| 4.3 | Образы без тега / latest | Поиск по кластеру или namespace | Python/Bash |
| 4.4 | Read-only проверки | Только чтение (get, list), без изменений | Python/Bash |
| 4.5 | Мульти-кластер | Переключение контекста, проверка нескольких кластеров | Bash/Python |

**Документ:** [docs/kubernetes.md](docs/kubernetes.md)

---

### 5. Argo CD

| # | Скрипт / раздел | Описание | Язык |
|---|-----------------|----------|------|
| 5.1 | Список приложений и статус | Sync/Health по всем приложениям | Python/Bash |
| 5.2 | Out-of-sync и ошибки | Поиск приложений с расхождениями или ошибками | Python/Bash |

**Документ:** [docs/argocd.md](docs/argocd.md)

---

### 6. Helm

| # | Скрипт / раздел | Описание | Язык |
|---|-----------------|----------|------|
| 6.1 | Валидация чартов | helm lint для выбранных чартов | Bash |
| 6.2 | Diff перед upgrade | Сравнение текущего состояния с чартом | Bash |
| 6.3 | Шаблоны values | Примеры values для dev/stage/prod | YAML + описание в docs |

**Документ:** [docs/helm.md](docs/helm.md)

---

### 7. GitLab CI/CD

Без связи с мониторингом — только пайплайны и примеры jobs.

| # | Раздел | Описание |
|---|--------|----------|
| 7.1 | Запуск диагностики | Job для запуска скриптов диагностики (артефакты отчётов) |
| 7.2 | Бэкапы по расписанию | Scheduled pipeline для бэкапов СУБД |
| 7.3 | Деплой через Helm | Пример deploy job (dev/stage/prod) |
| 7.4 | Snippets | Переиспользуемые фрагменты .gitlab-ci.yml с комментариями |

**Документ:** [docs/cicd-gitlab.md](docs/cicd-gitlab.md)

---

## Навигация по разделам

| Раздел | Папка скриптов | Документация |
|--------|----------------|--------------|
| Диагностика Linux | [scripts/system/](scripts/system/), [scripts/network/](scripts/network/) | [docs/diagnostics.md](docs/diagnostics.md) |
| Бэкапы СУБД | [scripts/backup/](scripts/backup/) | [docs/backups.md](docs/backups.md) |
| Troubleshooting СУБД | [scripts/database/](scripts/database/) | [docs/database-troubleshooting.md](docs/database-troubleshooting.md) |
| Восстановление | [scripts/restore/](scripts/restore/) | [docs/restore.md](docs/restore.md) |
| Kubernetes | [scripts/kubernetes/](scripts/kubernetes/) | [docs/kubernetes.md](docs/kubernetes.md) |
| Argo CD | [scripts/argocd/](scripts/argocd/) | [docs/argocd.md](docs/argocd.md) |
| Helm | [scripts/helm/](scripts/helm/) | [docs/helm.md](docs/helm.md) |
| GitLab CI/CD | [scripts/ci-cd/](scripts/ci-cd/) | [docs/cicd-gitlab.md](docs/cicd-gitlab.md) |

---

## Требования

- **ОС:** Ubuntu (скрипты ориентированы на неё).
- **Python:** 3.x (предпочтительно только стандартная библиотека).
- **Bash:** для обёрток, cron и вызовов kubectl / helm / argocd.
- **Инструменты:** по мере необходимости — kubectl, helm, argocd CLI, клиенты СУБД (pg_dump, mysqldump, mongodump и т.д.).

---

## Как пользоваться

1. Клонировать репозиторий.
2. Читать описание скриптов в README внутри каждой папки и в соответствующих `docs/*.md`.
3. Запускать скрипты локально или из GitLab CI по необходимости.
4. Адаптировать пути, учётные данные и расписания под своё окружение (учётные данные — через переменные окружения или секреты CI, не в коде).

Дальше — поэтапная реализация по разделам плана.
