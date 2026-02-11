# Диагностика системы (Linux / Ubuntu)

Скрипты для проверки ресурсов, диска, логов и сервисов. Язык: Python (стандартная библиотека).

| Скрипт | Описание |
|--------|----------|
| `system_summary.py` | Сводка: CPU, RAM, диск, load average, uptime |
| `disk_analysis.py` | Анализ диска: занятость, большие файлы/каталоги (`--dirs`, `--top N`) |
| `log_analysis.py` | Анализ логов: ошибки по паттерну, топ частых строк, `journalctl -p err`, ротация |
| `systemd_services.py` | Проверка systemd: failed/неактивные юниты, перезапуски, зависимости (`--unit NAME`) |
| `security_checks.py` | Базовые проверки: слушающие порты, права на /etc/shadow, SSH-ключи |

## Примеры

```bash
# Сводка по системе (диск по умолчанию для /)
python3 system_summary.py
python3 system_summary.py /var

# Топ 30 больших файлов в /var
python3 disk_analysis.py /var --top 30

# Топ 20 каталогов по размеру (медленно на больших деревьях)
python3 disk_analysis.py /var --dirs --top 20

# Ошибки в journald
python3 log_analysis.py --journal

# Ошибки в файлах логов и топ частых строк
python3 log_analysis.py /var/log --top 15

# Проверка logrotate
python3 log_analysis.py --rotation

# Failed-юниты systemd
python3 systemd_services.py --failed

# Статус и зависимости сервиса
python3 systemd_services.py --unit nginx.service

# Базовые проверки безопасности
python3 security_checks.py --all
```

**Документация:** [../../docs/diagnostics.md](../../docs/diagnostics.md)
