# Kubernetes

Проверки здоровья кластера, ресурсов, образов. Read-only и мульти-кластер. Требуется `kubectl` и настроенный kubeconfig.

| Скрипт | Описание |
|--------|----------|
| `k8s_common.py` | Общие вызовы kubectl (run, run_json) |
| `k8s_health.py` | Здоровье: ноды, поды, события, поды с рестартами |
| `k8s_resources.py` | Сводка requests/limits по namespace, опционально kubectl top |
| `k8s_images.py` | Поды с образами :latest или без тега |
| `k8s_readonly.py` | Набор только read-only проверок (get/list) |
| `k8s_multi_cluster.py` | Список контекстов, запуск проверки по каждому (--run-health) |

Во всех скриптах поддерживаются `--context` и `--kubeconfig`. Используются только операции чтения (get, list).

## Примеры

```bash
# Здоровье текущего кластера
python3 k8s_health.py
python3 k8s_health.py -n my-namespace --no-events

# Ресурсы по namespace + kubectl top (если есть metrics-server)
python3 k8s_resources.py --top
python3 k8s_resources.py -n default

# Образы :latest или без тега
python3 k8s_images.py
python3 k8s_images.py -n production

# Только read-only проверки (подходит для ограниченных ролей)
python3 k8s_readonly.py

# Несколько кластеров
python3 k8s_multi_cluster.py
python3 k8s_multi_cluster.py --run-health
python3 k8s_multi_cluster.py --contexts dev,prod --run-health
```

Переменные: `KUBECONFIG`, `KUBECTL` (путь к kubectl).

**Документация:** [../../docs/kubernetes.md](../../docs/kubernetes.md)
