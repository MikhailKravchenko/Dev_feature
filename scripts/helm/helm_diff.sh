#!/usr/bin/env bash
# Diff перед helm upgrade: сравнение текущего состояния в кластере с тем, что получится после upgrade.
# Требуется плагин helm-diff: helm plugin install https://github.com/databus23/helm-diff
# Использование:
#   ./helm_diff.sh <release> <chart> [--namespace N] [--values file.yaml]
#   ./helm_diff.sh myapp ./my-chart -n default -f values-prod.yaml
# Команда выполняет: helm diff upgrade <release> <chart> [опции]

set -e

HELM="${HELM:-helm}"
RELEASE=""
CHART=""
NAMESPACE=""
VALUES=""
EXTRA=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    -n|--namespace)
      NAMESPACE="$2"
      shift 2
      ;;
    -f|--values)
      VALUES="$2"
      shift 2
      ;;
    *)
      if [[ -z "$RELEASE" ]]; then
        RELEASE="$1"
      elif [[ -z "$CHART" ]]; then
        CHART="$1"
      else
        EXTRA+=("$1")
      fi
      shift
      ;;
  esac
done

if [[ -z "$RELEASE" || -z "$CHART" ]]; then
  echo "Использование: $0 <release> <chart> [--namespace N] [--values file.yaml] [--set key=val ...]" >&2
  echo "  release — имя релиза в кластере" >&2
  echo "  chart   — путь к чарту или имя (например stable/app)" >&2
  exit 1
fi

CMD=("$HELM" "diff" "upgrade" "$RELEASE" "$CHART")
[[ -n "$NAMESPACE" ]] && CMD+=(--namespace "$NAMESPACE")
[[ -n "$VALUES" ]] && CMD+=(--values "$VALUES")
CMD+=("${EXTRA[@]}")

echo "=== helm diff upgrade $RELEASE $CHART ==="
echo "  Выполняется: ${CMD[*]}"
echo ""
"${CMD[@]}"
