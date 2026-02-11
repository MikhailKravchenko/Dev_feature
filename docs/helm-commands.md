# Справочник: консольные команды Helm

Краткий справочник команд `helm` с пояснениями. Для работы с кластером нужен настроенный kubectl/kubeconfig.

---

## Репозитории

| Команда | Пояснение |
|---------|-----------|
| `helm repo add <name> <url>` | Добавить репозиторий чартов (например `helm repo add bitnami https://charts.bitnami.com/bitnami`). |
| `helm repo list` | Список добавленных репозиториев. |
| `helm repo update` | Обновить кэш репозиториев (получить актуальные версии чартов). |
| `helm repo remove <name>` | Удалить репозиторий из списка. |
| `helm search repo <keyword>` | Поиск чартов в добавленных репозиториях. |
| `helm search repo <name> --versions` | Все версии чарта. |

---

## Установка и обновление

| Команда | Пояснение |
|---------|-----------|
| `helm install <release> <chart>` | Установить релиз из чарта (chart — путь к каталогу, имя репозитория/чарта, например `bitnami/nginx`). |
| `helm install <release> <chart> -n <namespace>` | Установка в указанный namespace (namespace создаётся при необходимости с флагом `--create-namespace`). |
| `helm upgrade --install <release> <chart>` | Установить или обновить релиз (идемпотентная операция, удобно для CI/CD). |
| `helm upgrade <release> <chart> -f values.yaml` | Обновить релиз, переопределив values из файла. |
| `helm upgrade <release> <chart> --set key=value` | Переопределить один или несколько параметров в командной строке. |
| `helm upgrade <release> <chart> --set-file key=path` | Установить значение из файла (например сертификат). |
| `helm upgrade <release> <chart> --wait` | Ждать, пока поды станут Ready (по умолчанию helm не ждёт). |
| `helm upgrade <release> <chart> --timeout 5m` | Таймаут операции (по умолчанию 5m). |
| `helm upgrade <release> <chart> --dry-run --debug` | Показать сгенерированные манифесты без применения (проверка шаблонов). |
| `helm install <release> <chart> --create-namespace -n <ns>` | Создать namespace, если не существует, и установить в него. |

---

## Список и история

| Команда | Пояснение |
|---------|-----------|
| `helm list` | Список установленных релизов в текущем namespace. |
| `helm list -A` | Релизы во всех namespace. |
| `helm list -a` | Включая неудалённые релизы в статусе failed/pending-uninstall. |
| `helm list -o table` | Табличный вывод (по умолчанию). |
| `helm list -o json` | Вывод в JSON. |
| `helm history <release>` | История ревизий релиза (как при rollout). |
| `helm status <release>` | Статус релиза: последний деплой, описание, ресурсы. |
| `helm get manifest <release>` | Вывести все манифесты, которые были применены для релиза. |
| `helm get values <release>` | Вывести values, использованные при последнем установке/обновлении. |
| `helm get values <release> -a` | Все values (включая значения по умолчанию из чарта). |

---

## Откат и удаление

| Команда | Пояснение |
|---------|-----------|
| `helm rollback <release> [revision]` | Откатить релиз к указанной ревизии (или к предыдущей). |
| `helm rollback <release> 1` | Откатить к ревизии 1. |
| `helm uninstall <release>` | Удалить релиз (ресурсы в кластере удаляются). |
| `helm uninstall <release> --keep-history` | Удалить релиз, но сохранить историю (для последующего rollback при переустановке — нестандартный сценарий). |
| `helm uninstall <release> -n <namespace>` | Удалить релиз из указанного namespace. |

---

## Шаблоны и валидация

| Команда | Пояснение |
|---------|-----------|
| `helm template <release> <chart>` | Сгенерировать манифесты из чарта без установки в кластер (локальный рендер). |
| `helm template <release> <chart> -f values.yaml` | Рендер с переопределением values. |
| `helm template <release> <chart> --debug` | Рендер с отладочной информацией. |
| `helm lint <path>` | Проверить чарт на ошибки (синтаксис, best practices). |
| `helm lint <path> --strict` | Более строгие проверки. |
| `helm dependency list <path>` | Список зависимостей чарта (из Chart.yaml). |
| `helm dependency update <path>` | Скачать и обновить зависимости (из charts/). |
| `helm package <path>` | Упаковать чарт в .tgz архив. |

---

## Diff (плагин helm-diff)

Плагин: `helm plugin install https://github.com/databus23/helm-diff`

| Команда | Пояснение |
|---------|-----------|
| `helm diff upgrade <release> <chart>` | Показать diff между текущим состоянием релиза в кластере и тем, что получится после upgrade. |
| `helm diff upgrade <release> <chart> -f values.yaml` | С учётом переопределённых values. |
| `helm diff upgrade <release> <chart> -n <namespace>` | Для релиза в указанном namespace. |
| `helm diff rollback <release> [revision]` | Diff при откате к указанной ревизии. |

---

## Переменные и values

| Команда | Пояснение |
|---------|-----------|
| `helm install ... -f values.yaml` | Основной файл values. |
| `helm install ... -f values.yaml -f overrides.yaml` | Несколько файлов: последующие переопределяют предыдущие. |
| `helm install ... --set image.tag=abc123` | Одна переменная. |
| `helm install ... --set 'nested.key=value'` | Вложенный ключ. |
| `helm install ... --set-file tls.crt=./cert.pem` | Значение из файла. |
| `helm install ... --set-string tag=latest` | Строка без приведения типа. |
| `helm get values <release>` | Посмотреть, какие values применены к установленному релизу. |

---

## Окружение и kubeconfig

| Команда | Пояснение |
|---------|-----------|
| `helm list --kube-context <context>` | Список релизов в другом контексте. |
| `helm upgrade ... --kube-context <context>` | Выполнить upgrade в указанном контексте. |
| Переменная `KUBECONFIG` | Путь к kubeconfig (как для kubectl). |
| Переменная `HELM_KUBECONTEXT` | Контекст по умолчанию для helm. |

---

## Краткие примеры

```bash
# Установить nginx из Bitnami в namespace production
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install my-nginx bitnami/nginx -n production --create-namespace

# Обновить с новым values и подождать готовности
helm upgrade --install myapp ./my-chart -f values-prod.yaml -n production --wait

# Посмотреть, что изменится
helm diff upgrade myapp ./my-chart -f values-prod.yaml -n production

# Откатить к предыдущей версии
helm rollback myapp -n production

# Удалить релиз
helm uninstall myapp -n production
```

---

Вернуться к разделу [Helm](helm.md) и [скриптам](../scripts/helm/).
