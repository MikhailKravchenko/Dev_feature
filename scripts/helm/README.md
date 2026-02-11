# Helm

Валидация чартов, diff перед upgrade, примеры values по окружениям.

| Скрипт / каталог | Описание |
|------------------|----------|
| `helm_lint.sh` | Запуск helm lint для текущего каталога или указанных путей к чартам |
| `helm_diff.sh` | helm diff upgrade (нужен плагин helm-diff): сравнение с состоянием в кластере |
| `values-examples/` | Примеры values для dev, stage, prod (replicaCount, resources, ingress, env) |

## Требования

- **helm**
- Для diff: плагин **helm-diff** — `helm plugin install https://github.com/databus23/helm-diff`

## Примеры

```bash
chmod +x helm_lint.sh helm_diff.sh

# Валидация чарта в текущем каталоге
./helm_lint.sh

# Валидация нескольких чартов
./helm_lint.sh ./chart1 ./chart2

# Diff перед upgrade (что изменится в кластере)
./helm_diff.sh myrelease ./my-chart -n production
./helm_diff.sh myrelease ./my-chart -n production -f values-examples/values-prod.yaml

# Деплой с values по окружению
helm upgrade --install myapp ./chart -f values-examples/values-prod.yaml -n production
```

Переменная **HELM** — путь к helm (по умолчанию `helm`).

**Документация:** [../../docs/helm.md](../../docs/helm.md) · **Справочник команд helm:** [../../docs/helm-commands.md](../../docs/helm-commands.md)
