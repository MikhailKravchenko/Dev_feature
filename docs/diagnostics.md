# Диагностика и траблшутинг Linux (Ubuntu)

Документация по скриптам диагностики системы и сети.

**Скрипты:** [../scripts/system/](../scripts/system/), [../scripts/network/](../scripts/network/)

---

## Система (scripts/system/)

| Скрипт | Назначение |
|--------|------------|
| `system_summary.py` | Сводка: хост, uptime, load average, CPU, память, занятость диска (по пути, по умолчанию `/`). Только чтение `/proc` и `os.statvfs`. |
| `disk_analysis.py` | Занятость по пути; топ N больших файлов или каталогов (`--top`, `--dirs`), опционально ограничение глубины `--depth`. |
| `log_analysis.py` | Поиск по паттерну (по умолчанию ERROR/CRITICAL/Fail и т.д.) в файлах или через `journalctl -p err`; топ частых строк; проверка наличия конфигов logrotate. |
| `systemd_services.py` | Failed/неактивные юниты; юниты с перезапусками; список загруженных сервисов; для одного юнита — статус и зависимости (`--unit NAME`). |
| `security_checks.py` | Слушающие порты (`ss -tuln`); права на `/etc/shadow`, `/etc/passwd`, SSH-ключи и т.д. Только чтение; при замечаниях — код выхода 1. |

## Сеть (scripts/network/)

| Скрипт | Назначение |
|--------|------------|
| `network_checks.py` | Порты (`ss -tuln`), установленные TCP-соединения (`ss -tn state established`), DNS (`--dns NAME`), HTTP HEAD (`--http URL`). Без аргументов — порты + соединения. |

---

## Примеры вызова

```bash
# Быстрая сводка по системе
python3 scripts/system/system_summary.py

# Большие файлы в /var, топ 30
python3 scripts/system/disk_analysis.py /var --top 30

# Ошибки в journald
python3 scripts/system/log_analysis.py --journal

# Failed-сервисы systemd
python3 scripts/system/systemd_services.py --failed

# Проверка безопасности (порты + права на файлы)
python3 scripts/system/security_checks.py --all

# Сеть: порты и соединения
python3 scripts/network/network_checks.py

# DNS и HTTP
python3 scripts/network/network_checks.py --dns google.com --http https://google.com
```

---

## Требования

- Python 3.8+
- Linux (Ubuntu): доступ к `/proc`, `systemctl`, `ss` (пакет iproute2). Для `log_analysis.py --journal` — journald.
