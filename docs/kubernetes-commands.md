# Справочник: консольные команды Kubernetes (kubectl)

Краткий справочник команд `kubectl` с пояснениями. Для работы нужен настроенный kubeconfig (`KUBECONFIG` или `~/.kube/config`).

---

## Контекст и конфигурация

| Команда | Пояснение |
|---------|-----------|
| `kubectl config current-context` | Показать текущий контекст (какой кластер/пользователь активен). |
| `kubectl config get-contexts` | Список всех контекстов из kubeconfig. |
| `kubectl config use-context <name>` | Переключиться на указанный контекст. |
| `kubectl config view` | Вывести kubeconfig (без секретов по умолчанию). |
| `kubectl cluster-info` | Краткая информация о кластере и адресах API. |

---

## Namespace

| Команда | Пояснение |
|---------|-----------|
| `kubectl get ns` | Список всех namespace. |
| `kubectl get ns -o wide` | То же с дополнительными колонками. |
| `kubectl create ns <name>` | Создать namespace. |
| `kubectl config set-context --current --namespace=<name>` | Установить namespace по умолчанию для текущего контекста (все последующие команды без `-n` будут в этом ns). |

---

## Ноды

| Команда | Пояснение |
|---------|-----------|
| `kubectl get nodes` | Список нод и их статус (Ready и т.д.). |
| `kubectl get nodes -o wide` | Список нод с IP, ОС, версией kubelet, количеством подов. |
| `kubectl describe node <name>` | Подробная информация о ноде: ресурсы, условия, поды на ноде, тайнты/толерации. |
| `kubectl top nodes` | Использование CPU и памяти по нодам (нужен metrics-server). |

---

## Поды (pods)

| Команда | Пояснение |
|---------|-----------|
| `kubectl get pods` | Поды в текущем (или default) namespace. |
| `kubectl get pods -A` | Поды во всех namespace. |
| `kubectl get pods -n <ns>` | Поды в указанном namespace. |
| `kubectl get pods -o wide` | Доп. колонки: нода, IP пода. |
| `kubectl get pods -w` | Следить за изменениями в реальном времени (watch). |
| `kubectl describe pod <name>` | Подробное описание пода: события, контейнеры, условия, логи предыдущего инстанса (если был рестарт). |
| `kubectl logs <pod>` | Логи первого контейнера в поде. |
| `kubectl logs <pod> -c <container>` | Логи указанного контейнера. |
| `kubectl logs <pod> -f` | Стриминг логов (как tail -f). |
| `kubectl logs <pod> --previous` | Логи контейнера до последнего рестарта. |
| `kubectl exec -it <pod> -- /bin/sh` | Интерактивный shell в поде (зависит от образа: может быть /bin/bash). |
| `kubectl exec <pod> -c <container> -- <cmd>` | Выполнить команду в контейнере без входа в shell. |
| `kubectl delete pod <name>` | Удалить под (ReplicaSet/Deployment при необходимости создаст новый). |

---

## Deployments, ReplicaSets

| Команда | Пояснение |
|---------|-----------|
| `kubectl get deploy` | Список Deployment в текущем namespace. |
| `kubectl get rs` | Список ReplicaSet. |
| `kubectl describe deploy <name>` | Детали деплоймента: образ, реплики, стратегия, события. |
| `kubectl rollout status deploy/<name>` | Дождаться завершения текущего rollout (успех или таймаут). |
| `kubectl rollout history deploy/<name>` | История ревизий rollout. |
| `kubectl rollout undo deploy/<name>` | Откатить к предыдущей ревизии. |
| `kubectl rollout restart deploy/<name>` | Перезапуск подов деплоймента (новый rollout). |
| `kubectl scale deploy <name> --replicas=N` | Изменить количество реплик. |

---

## Сервисы и Ingress

| Команда | Пояснение |
|---------|-----------|
| `kubectl get svc` | Список Service в namespace. |
| `kubectl get svc -o wide` | С VC (ClusterIP/NodePort) и внешним IP для LoadBalancer. |
| `kubectl get ingress` | Список Ingress. |
| `kubectl describe svc <name>` | Подробно: эндпоинты (поды), порты, селекторы. |
| `kubectl describe ingress <name>` | Хосты, пути, бэкенды, события. |

---

## События и отладка

| Команда | Пояснение |
|---------|-----------|
| `kubectl get events` | События в текущем namespace (по времени). |
| `kubectl get events -A` | События во всех namespace. |
| `kubectl get events --sort-by=.lastTimestamp` | Сортировка по времени последнего события. |
| `kubectl get events -A --field-selector type=Warning` | Только предупреждения. |
| `kubectl top pods` | Использование CPU/памяти по подам (metrics-server). |
| `kubectl top pods -A` | По всем namespace. |
| `kubectl get pods -o json \| jq '.items[] | select(.status.containerStatuses[]?.restartCount > 0)'` | Поды с рестартами (при наличии jq). |

---

## Ресурсы (YAML, вывод)

| Команда | Пояснение |
|---------|-----------|
| `kubectl get <resource> -o yaml` | Вывести ресурс в YAML (например `kubectl get pod mypod -o yaml`). |
| `kubectl get <resource> -o json` | Вывод в JSON. |
| `kubectl get <resource> -o name` | Только имена (удобно для xargs). |
| `kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName` | Свои колонки. |
| `kubectl apply -f file.yaml` | Создать/обновить ресурсы из манифеста. |
| `kubectl delete -f file.yaml` | Удалить ресурсы, описанные в манифесте. |
| `kubectl diff -f file.yaml` | Показать diff между манифестом и текущим состоянием в кластере. |

---

## Полезные алиасы (опционально)

Добавьте в `~/.bashrc` или `~/.zshrc`:

```bash
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgpa='kubectl get pods -A'
alias kdp='kubectl describe pod'
alias kl='kubectl logs'
alias kx='kubectl exec -it'
```

После этого: `k get pods`, `kgpa`, `kl mypod -f` и т.д.

---

Вернуться к разделу [Kubernetes](kubernetes.md) и [скриптам](../scripts/kubernetes/).
