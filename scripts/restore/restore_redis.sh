#!/usr/bin/env bash
# Восстановление Redis из RDB-бэкапа: подмена dump.rdb и перезапуск сервиса.
# Запуск может требовать прав на запись в каталог данных и systemctl (sudo).
# Использование:
#   ./restore_redis.sh --backup /backup/redis/redis_2025-02-11.rdb [--rdb-path /var/lib/redis/dump.rdb] [--restart]
#   --restart  выполнить systemctl restart redis-server (или redis)

set -e

RDB_PATH="${RDB_PATH:-/var/lib/redis/dump.rdb}"
RESTART=""
REDIS_SERVICE="${REDIS_SERVICE:-redis-server}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --backup|-b)
      BACKUP="$2"
      shift 2
      ;;
    --rdb-path)
      RDB_PATH="$2"
      shift 2
      ;;
    --restart)
      RESTART=1
      shift
      ;;
    *)
      echo "Неизвестный аргумент: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$BACKUP" ]]; then
  echo "Укажите --backup /path/to/file.rdb" >&2
  exit 1
fi

if [[ ! -f "$BACKUP" ]]; then
  echo "Файл бэкапа не найден: $BACKUP" >&2
  exit 1
fi

RDB_DIR="$(dirname "$RDB_PATH")"
if [[ ! -d "$RDB_DIR" ]]; then
  echo "Каталог данных Redis не найден: $RDB_DIR" >&2
  exit 1
fi

echo "=== Восстановление Redis из RDB ==="
echo "  Бэкап:    $BACKUP"
echo "  Целевой: $RDB_PATH"
echo ""

# Остановить Redis перед подменой файла (чтобы он не перезаписал бэкап при выходе)
if [[ -n "$RESTART" ]]; then
  echo "Остановка Redis..."
  systemctl stop "$REDIS_SERVICE" || true
fi

# Бэкап текущего dump.rdb (если есть)
if [[ -f "$RDB_PATH" ]]; then
  SAVE="${RDB_PATH}.before_restore.$(date +%Y%m%d_%H%M%S)"
  echo "Сохранение текущего RDB в $SAVE"
  mv "$RDB_PATH" "$SAVE"
fi

echo "Копирование бэкапа в $RDB_PATH"
cp "$BACKUP" "$RDB_PATH"
chown redis:redis "$RDB_PATH" 2>/dev/null || true
chmod 660 "$RDB_PATH" 2>/dev/null || true

if [[ -n "$RESTART" ]]; then
  echo "Запуск Redis..."
  systemctl start "$REDIS_SERVICE"
  echo "Готово. Redis перезапущен."
else
  echo "Готово. Файл подменён. Для применения перезапустите Redis вручную: systemctl restart $REDIS_SERVICE"
fi
