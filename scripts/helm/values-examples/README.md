# Шаблоны values по окружениям

Примеры структуры values для **dev**, **stage**, **prod**. Используйте как основу и подстройте под свой чарт (имена ключей зависят от шаблонов чарта).

| Файл | Назначение |
|------|------------|
| `values-dev.yaml` | Одна реплика, меньшие ресурсы, отладка (LOG_LEVEL=debug), ingress часто выключен. |
| `values-stage.yaml` | 2 реплики, средние ресурсы, ingress для тестирования. |
| `values-prod.yaml` | 3 реплики, увеличенные ресурсы, LOG_LEVEL=warn. |

## Отличия по окружениям

- **replicaCount**: dev 1, stage 2, prod 3 (или больше).
- **resources**: растут от dev к prod.
- **ingress**: в dev часто отключён или один хост; в stage/prod включён со своими хостами.
- **env / LOG_LEVEL**: dev debug, stage info, prod warn (или error).

Деплой с указанием values:

```bash
helm upgrade --install myapp ./chart -f values-examples/values-prod.yaml -n production
```
