#!/usr/bin/env bash
# Валидация Helm-чартов: helm lint для указанных каталогов или текущего.
# Использование:
#   ./helm_lint.sh                    # lint в текущем каталоге (ожидается Chart.yaml)
#   ./helm_lint.sh path/to/chart       # один чарт
#   ./helm_lint.sh chart1 chart2 ...   # несколько чартов
# Команда выполняет: helm lint <path> для каждого пути.

set -e

HELM="${HELM:-helm}"
EXIT=0

if [[ $# -eq 0 ]]; then
  # Текущий каталог
  echo "=== helm lint . ==="
  if "$HELM" lint . ; then
    echo "  OK"
  else
    EXIT=1
  fi
else
  for path in "$@"; do
    if [[ ! -d "$path" ]]; then
      echo "Ошибка: каталог не найден: $path" >&2
      EXIT=1
      continue
    fi
    echo "=== helm lint $path ==="
    if "$HELM" lint "$path"; then
      echo "  OK: $path"
    else
      EXIT=1
    fi
    echo ""
  done
fi

exit "$EXIT"
