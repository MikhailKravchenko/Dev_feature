# Kubernetes

Скрипты для работы с одним или несколькими кластерами. Только **чтение** (get/list); подходят для ролей с ограниченным доступом.

**Скрипты:** [../scripts/kubernetes/](../scripts/kubernetes/)

---

## Скрипты

| Скрипт | Назначение |
|--------|------------|
| `k8s_health.py` | Ноды (get nodes -o wide), поды по namespace, события (get events), поды с ненулевым restartCount. |
| `k8s_resources.py` | Сводка requests/limits по namespace из манифестов подов; опционально `kubectl top nodes` и `kubectl top pods` (нужен metrics-server). |
| `k8s_images.py` | Поиск подов с образами с тегом `:latest` или без тега (только имя образа). |
| `k8s_readonly.py` | Набор проверок только через get/list (nodes, ns, pods) — для ролей без прав на изменение. |
| `k8s_multi_cluster.py` | Список контекстов (`kubectl config get-contexts`); с `--run-health` — запуск `k8s_health.py` для каждого контекста. Опция `--contexts ctx1,ctx2` — только выбранные контексты. |

Во всех скриптах: `--context`, `--kubeconfig`, при необходимости `--namespace`.

---

## Требования

- **kubectl**, настроенный kubeconfig (или `KUBECONFIG`).
- Для read-only достаточно роли с правами `get`, `list` на соответствующие ресурсы.
- Для `k8s_resources.py --top` нужен установленный **metrics-server** в кластере.

---

## Примеры

```bash
# Текущий кластер
python3 scripts/kubernetes/k8s_health.py
python3 scripts/kubernetes/k8s_resources.py --top

# Конкретный контекст
python3 scripts/kubernetes/k8s_health.py --context prod

# Несколько кластеров подряд
python3 scripts/kubernetes/k8s_multi_cluster.py --run-health
```
