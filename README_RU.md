[English README](README.md) | [Russian README](README_RU.md)

# CineCLI v0.2.6

CLI-инструмент для поиска и стриминга фильмов с Rutracker прямо в вашем терминале с помощью mpv и webtorrent.

## Возможности

- Поиск торрентов на Rutracker прямо из терминала
- Прямой стриминг в mpv без скачивания файлов на диск
- Генерация magnet-ссылок с несколькими трекерами для быстрого старта
- Интерактивный режим для удобного просмотра и выбора
- Гибкая настройка с поддержкой cookies браузера
- Умный выбор торрента — автоматически отдаёт предпочтение 1080p, высокому числу сидов, релизам WebRip/BDRip

## Требования

- Python 3.10+ (протестировано на 3.14)
- webtorrent — установлен глобально
- mpv — медиаплеер для стриминга
- Node.js (необходим для установки webtorrent)

## Установка

### Шаг 1: Python-пакет

```bash
pip install cinecli-ru
```

### Шаг 2: Системные зависимости

#### macOS

```bash
brew install mpv
npm install -g webtorrent
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get install mpv npm
sudo npm install -g webtorrent
```

#### Linux (Fedora/RHEL)

```bash
sudo dnf install mpv npm
sudo npm install -g webtorrent
```

### Шаг 3: Настройка

Создайте файл `~/.config/cinecli/config.toml`:

```bash
mkdir -p ~/.config/cinecli
```

#### Вариант А: Логин + пароль

```toml
[rutracker]
username = "ваш_логин"
password = "ваш_пароль"

[settings]
default_limit = 20
```

#### Вариант Б: Cookies браузера (рекомендуется)

Более надёжный способ — использовать cookies из вашего браузера.

1. Откройте rutracker.org и войдите в аккаунт
2. Откройте DevTools (F12)
3. Перейдите в Application → Cookies → rutracker.org
4. Скопируйте все cookies сайта (нужны: `bb_guid`, `bb_session`, `bb_ssl`, `bb_t`, `bb_clearance`)
5. Добавьте их в конфиг:

```toml
[rutracker]
username = "ваш_логин"
password = "ваш_пароль"
cookie = "bb_guid=XXX; bb_session=YYY; bb_ssl=1; bb_t=ZZZ; bb_clearance=WWW"

[settings]
default_limit = 20
```

Совет: Вы можете использовать расширение для браузера для автоматического экспорта cookies.

## Использование

### Поиск торрентов

```bash
cinecli-ru search matrix
cinecli-ru search "enemy at the gates" --limit 10
cinecli-ru search avatar -n 5
```

### Смотреть сразу (основная команда)

Выполняет поиск, автоматически выбирает лучший торрент и запускает стриминг.

```bash
cinecli-ru watch matrix
cinecli-ru watch dune --limit 10
```

Выбор может быть ручным, если автовыбор отключён в запросе.

### Информация о торренте и действия

Открывает конкретный торрент (по topic_id) и предлагает выбрать действие.

```bash
cinecli get 6677988
```

Доступные действия:

- stream — прямой стриминг в mpv через webtorrent
- magnet — открыть magnet-ссылку в торрент-клиенте (qBittorrent, Transmission и др.)
- page — открыть страницу торрента в браузере
- skip — отмена и выход

### Интерактивный режим

```bash
cinecli-ru interactive
```

Как это работает:

1. Введите название фильма
2. Просмотрите таблицу результатов
3. Выберите автоматический выбор (лучший по сидам) или выберите вручную
4. Выберите действие (stream, magnet или page)

## Параметры команд

### `search` и `watch`

- `--limit N` или `-n N` — максимальное количество результатов (по умолчанию: 20)

Примеры:

```bash
cinecli-ru search "blade runner" --limit 5
cinecli-ru watch inception -n 15
```

## Качество стриминга

Инструмент автоматически отдаёт предпочтение торрентам, подходящим для стриминга.

Приоритет:

- Разрешение 1080p
- Форматы WebRip, BDRip (~2–4 ГБ для быстрого старта)
- Высокое число сидов

Избегаются:

- Крупные remux-релизы (>10 ГБ, медленная буферизация)
- Слишком большие UHD или Blu-ray рипы

Совет: Для лучшего опыта выбирайте WebRip или BDRip релизы около 2–4 ГБ.

## Устранение неполадок

### Ошибка аутентификации

Проблема: "Rutracker login failed" или возвращается страница входа.

Решение:

1. Проверьте логин и пароль
2. Попробуйте использовать cookies браузера (более надёжно)
3. Убедитесь, что сайт доступен
4. Обновите cookies — они могут истечь

### webtorrent не найден

```bash
npm install -g webtorrent
webtorrent --version
```

### mpv не найден

- macOS: `brew install mpv`
- Ubuntu: `sudo apt-get install mpv`
- Fedora: `sudo dnf install mpv`

### Медленный стриминг

- Проверьте интернет-соединение
- Выбирайте торренты с большим числом сидов
- Используйте `cinecli get <id>` и выберите файл поменьше (WebRip)
- Избегайте крупных remux-релизов для стриминга

### API недоступен

Если вы видите предупреждение об API, сервер Rutracker может быть временно недоступен. Инструмент автоматически переключится на парсинг веб-интерфейса (работает, но может быть медленнее).

## Настройка

### Расположение файла конфигурации

- Linux/macOS: `~/.config/cinecli/config.toml`
- Windows: `%APPDATA%\cinecli\config.toml`

### Полный пример конфигурации

```toml
[rutracker]
username = "ваш_логин"
password = "ваш_пароль"
cookie = ""

[settings]
default_limit = 20
```

## Разработка

### Сборка из исходников

```bash
git clone https://github.com/yourusername/cinecli
cd cinecli
pip install -e .
```

### Зависимости проекта

- typer — CLI-фреймворк
- rich — форматированный вывод в терминале (таблицы, панели)
- rutracker-api — клиент API Rutracker
- beautifulsoup4 — парсинг HTML
- requests — HTTP-запросы
- lxml — парсер для BeautifulSoup

### Разработка и тестирование

```bash
pip install -e ".[dev]"
pytest
black .
ruff .
```

## Примеры использования

### Сценарий 1: Быстро посмотреть фильм

```bash
$ cinecli watch matrix
Searching: matrix

Auto-select (most seeds)? [Y/n]: y

Selected: The Matrix (1999) 1080p WEB-DL [10 seeds, 2.3 GB]

Streaming: The Matrix (1999) 1080p WEB-DL
```

### Сценарий 2: Ручной выбор

```bash
$ cinecli watch dune

Auto-select (most seeds)? [Y/n]: n
Select number [0-19]: 5
```

### Сценарий 3: Получить magnet-ссылку для торрент-клиента

```bash
$ cinecli-ru get 6677988

Action [stream/magnet/page/skip]: magnet

Magnet link opened in torrent client
```

## Правовое уведомление

Этот инструмент предназначен исключительно для личного законного использования с контентом, доступ к которому вы имеете право осуществлять на законных основаниях. Пожалуйста, соблюдайте законодательство об авторском праве в вашей юрисдикции.

---

Version: 0.1.5  
Python: 3.10+  
License: MIT
