# Сетевые проверки

Скрипты для диагностики сети: порты, соединения, DNS, HTTP. Язык: Python (стандартная библиотека + вызов `ss`).

| Скрипт | Описание |
|--------|----------|
| `network_checks.py` | Порты (ss -tuln), установленные TCP-соединения, DNS-резолв, HTTP HEAD-проверка |

## Примеры

```bash
# Сводка: порты + установленные соединения
python3 network_checks.py

# Только слушающие порты
python3 network_checks.py --ports

# DNS-резолв
python3 network_checks.py --dns example.com

# Проверка доступности URL
python3 network_checks.py --http https://example.com
```

**Требования:** утилита `ss` (пакет iproute2, обычно есть на Ubuntu).

**Документация:** [../../docs/diagnostics.md](../../docs/diagnostics.md)
