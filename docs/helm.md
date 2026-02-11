# Helm

Валидация чартов, сравнение с кластером перед upgrade, шаблоны values по окружениям.

**Скрипты и примеры:** [../scripts/helm/](../scripts/helm/)

---

## Скрипты

| Скрипт | Назначение |
|--------|------------|
| `helm_lint.sh` | **helm lint** для текущего каталога (ожидается Chart.yaml) или для переданных путей к чартам. Несколько путей — lint по очереди. |
| `helm_diff.sh` | **helm diff upgrade** &lt;release&gt; &lt;chart&gt; с опциями --namespace, --values. Показывает, что изменится в кластере после upgrade. Требуется плагин [helm-diff](https://github.com/databus23/helm-diff): `helm plugin install https://github.com/databus23/helm-diff`. |

## Шаблоны values

В каталоге **values-examples/** приведены примеры values для окружений:

| Файл | Описание |
|------|----------|
| `values-dev.yaml` | 1 реплика, меньшие ресурсы, отладка (LOG_LEVEL=debug), ingress часто выключен. |
| `values-stage.yaml` | 2 реплики, средние ресурсы, ingress для тестирования. |
| `values-prod.yaml` | 3 реплики, увеличенные ресурсы, продакшен-уровень логов. |

Структура (replicaCount, resources, ingress, env) — пример; подстройте под свой чарт.

---

## Примеры

```bash
# Lint
./scripts/helm/helm_lint.sh
./scripts/helm/helm_lint.sh ./my-chart

# Diff перед upgrade
./scripts/helm/helm_diff.sh myapp ./my-chart -n default -f values-examples/values-prod.yaml

# Установка с values
helm upgrade --install myapp ./my-chart -f scripts/helm/values-examples/values-prod.yaml -n production
```

Требования: **helm**; для diff — плагин **helm-diff**.
