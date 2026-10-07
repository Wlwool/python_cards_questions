# Python Cards Questions

[![Tests](https://github.com/Wlwool/python_cards_questions/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/Wlwool/python_cards_questions/actions/workflows/tests.yml)

Карточки "вопрос - ответ - пример кода" для подготовки к собеседованиям по Python. Проект состоит из трёх частей:
- **бот** присылает серию карточек по расписанию в Telegram и Discord;
- **backend** (REST API) хранит карточки и отдаёт их с поиском, фильтрами и пагинацией;
- **frontend** показывает карточки на сайте.

## Содержание

- [Стек](#стек)
- [Структура проекта](#структура-проекта)
- [Быстрый старт](#быстрый-старт)
- [Настройка (.env)](#настройка-env)
- [Как работает бот](#как-работает-бот)
- [API](#api)
- [Импорт карточек из Markdown](#импорт-карточек-из-markdown)
- [Разработка без Docker](#разработка-без-docker)
- [Тесты и линтер](#тесты-и-линтер)
- [Обновление бота на сервере](#обновление-бота-на-сервере)

## Стек

| Часть | Технологии |
|-------|-----------|
| Бот | Python 3.13, aiogram 3, APScheduler, aiohttp (Discord webhook), SQLAlchemy |
| Backend | FastAPI, SQLAlchemy, SQLite, JWT (PyJWT), pydantic-settings |
| Frontend | Vue 3, Vite, Pinia, highlight.js |
| Инфраструктура | Docker Compose, Nginx |
| Инструменты | uv, pytest, ruff, GitHub Actions |

## Структура проекта

```
backend/
  app/
    routers/          cards.py (публичное API), admin.py (CRUD, нужен токен)
    scripts/          migrate_md.py, questions.md, new_questions.md
    auth.py config.py database.py main.py models.py schemas.py
  tests/
bot/
  main.py             расписание, отправка серий, команды бота
  cards.py            выбор карточек и форматирование под Telegram и Discord
  discord_sender.py   отправка через webhook с повторами
  state.py            хранение номера последней отправленной карточки
  config.py           чтение переменных окружения
  tests/
frontend/
docker-compose.yml
.env.example
```

Backend и бот используют одну базу SQLite через общий том Docker (`sqlite_data`). Бот только читает карточки, записывает их backend (через API или скрипт импорта).

## Быстрый старт
 
````bash
cp .env.example .env
# заполните значения, см. раздел «Настройка»
 
docker compose up -d --build
````
 
Загрузить карточки в базу:
 
````bash
docker compose exec -e PYTHONPATH=/app backend uv run python app/scripts/migrate_md.py --file app/scripts/questions.md
````
 
Сайт доступен на http://localhost:8080.
 
Если порт 8080 занят или на сервере уже есть свой Nginx, измените порт в блоке `ports` сервиса `frontend` в `docker-compose.yml`. На сервере, где работает только бот, этот блок можно закомментировать.
 
Запустить только бота:
 
````bash
docker compose up -d --no-deps bot
````
 
Без `--no-deps` вместе с ботом поднимется и backend, от которого он зависит в compose.
 
**Важно:** при старте бот сразу отправляет серию карточек, не дожидаясь расписания. Каждый перезапуск контейнера бота запускает рассылку.
 
Логи:
 
````bash
docker compose logs -f bot
docker compose logs -f backend
````

## Настройка (.env)

Файл `.env` не попадает в Git. Шаблон: `.env.example`.

### Бот

| Переменная | Обязательна | По умолчанию | Назначение |
|------------|-------------|--------------|-----------|
| `BOT_TOKEN` | да | нет | токен Telegram-бота |
| `ADMIN_IDS` | да | нет | id пользователей Telegram через запятую; только они могут пользоваться командами бота и получают рассылку |
| `TELEGRAM_ENABLED` | нет | `true` | `false` отключает отправку в Telegram |
| `DISCORD_WEBHOOK_URL` | нет | пусто | webhook канала Discord; если пусто, Discord отключён, в лог пишется предупреждение |
| `CARDS_PER_SESSION` | нет | `4` | сколько карточек в одной серии |
| `PAUSE_BETWEEN_CARDS_SECONDS` | нет | `240` | пауза между карточками в серии, секунды |
| `DATABASE_URL` | нет | `sqlite:///./data/cards.db` | путь к базе карточек |

Бот не запустится, если отключены оба канала (`TELEGRAM_ENABLED=false` и пустой `DISCORD_WEBHOOK_URL`): отправлять было бы некуда. Переменные `BOT_TOKEN` и `ADMIN_IDS` проверяются при старте всегда, даже если Telegram отключён.

### Backend

| Переменная | Обязательна | Назначение |
|------------|-------------|-----------|
| `ADMIN_PASSWORD` | да | пароль администратора |
| `SECRET_KEY` | да | ключ подписи JWT-токенов |

Пустые значения секретов отклоняются при старте. Задавайте длинный случайный `SECRET_KEY`, например: `python -c "import secrets; print(secrets.token_urlsafe(48))"`.

## Как работает бот

- **Расписание:** серия карточек отправляется в 7, 12, 17 и 22 часа (в Docker часовой пояс бота `Europe/Moscow`) и сразу при запуске.
- **Порядок:** карточки идут по возрастанию `id`; после последней список начинается заново. Номер последней отправленной карточки хранится в файле состояния `bot_state.json` и переживает перезапуск. Запись атомарная, обрыв посреди записи не портит файл.
- **Каналы:** Telegram и Discord работают параллельно. Ошибка Discord только логируется. Если не удалась отправка в Telegram, сохраняется прогресс и через 15 минут серия повторяется.
- **Длинные тексты:** сообщения режутся по границам строк с учётом лимитов (4096 символов в Telegram, 2000 в Discord). Код отправляется отдельным сообщением: в Telegram в блоке `<pre>`, в Discord в блоке ` ```python `.
- **Повторы:** Discord при ответе 429 ждёт столько, сколько просит сервер (с потолком), и делает ограниченное число попыток.
- **Команды** (только для `ADMIN_IDS`): `/card` присылает случайную карточку, `/start` выводит справку.
- **Битые данные:** если у карточки в базе повреждено поле `tags`, она всё равно отправляется, только без тегов, а в лог попадает предупреждение с её `id`.

## API

Документация (Swagger) доступна на `/docs` у запущенного backend.

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/health` | открытый | проверка работы сервиса |
| GET | `/api/cards` | открытый | список карточек |
| GET | `/api/cards/{id}` | открытый | одна карточка, `404` если нет |
| GET | `/api/cards/categories` | открытый | список категорий |
| POST | `/api/admin/login` | открытый | вход, возвращает JWT-токен |
| POST | `/api/admin/cards` | токен | создать карточку |
| PUT | `/api/admin/cards/{id}` | токен | обновить карточку |
| DELETE | `/api/admin/cards/{id}` | токен | удалить карточку |

Параметры `GET /api/cards`:

| Параметр | Описание |
|----------|----------|
| `search` | подстрока в вопросе или ответе, без учёта регистра (в том числе для кириллицы) |
| `category` | точное совпадение категории |
| `difficulty` | `easy`, `normal` или `hard` |
| `tags` | теги через запятую, например `list,dict`; находятся карточки хотя бы с одним из них, совпадение точное (`set` не находит `subset`) |
| `page` | номер страницы, от 1 |
| `per_page` | размер страницы, от 1 до 500, по умолчанию 20 |

Ответ списка: `items`, `total`, `page`, `per_page`.

Пример:

```bash
curl "http://localhost:8000/api/cards?search=декоратор&difficulty=normal&per_page=5"
```

Поля карточки: `question`, `answer`, `code_example`, `category`, `tags` (список строк), `difficulty`.

## Импорт карточек из Markdown

Скрипт `backend/app/scripts/migrate_md.py` разбирает Markdown-файл и добавляет карточки в базу.

### Формат файла

```markdown
# Категория
## Подкатегория (тоже становится категорией)
### Вопрос?
Текст ответа.

```python
print("пример кода")
```
```

- заголовки уровней 1 и 2 задают категорию;
- заголовки уровня 3 и глубже задают вопрос, текст под ним становится ответом;
- блоки кода попадают в `code_example`; если блоков несколько, они нумеруются комментариями `# Пример 1`, `# Пример 2`;
- импортированные карточки получают `difficulty = normal` и пустые теги, их можно поменять через API или админку.

### Запуск

Добавить карточки к существующим:

```bash
docker compose exec -e PYTHONPATH=/app backend uv run python app/scripts/migrate_md.py --file app/scripts/new_questions.md
```

Сначала удалить все карточки, затем импортировать (флаг `--clear`):

```bash
docker compose exec -e PYTHONPATH=/app backend uv run python app/scripts/migrate_md.py --file app/scripts/questions.md --clear
```

### Что делает скрипт

- **Дубли пропускаются.** Карточка считается дублем, если в базе или раньше в этом же файле уже есть такая же пара вопрос + категория. Повторный запуск без `--clear` безопасен. В конце скрипт пишет, сколько карточек добавлено и сколько пропущено.
- **Незакрытые блоки кода.** Если в файле остался незакрытый блок ` ``` `, перед импортом в консоль выводятся строки `ВНИМАНИЕ: ...` с названием вопроса и категории. Карточки при этом импортируются, предупреждение нужно, чтобы найти и поправить проблемное место. Проверка эвристическая: незакрытый блок с голой оградой в середине файла она может не заметить.
- Пустые вопросы и ответы пропускаются.

## Разработка без Docker

Нужны Python 3.13, [uv](https://docs.astral.sh/uv/) и Node.js.

```bash
# backend (API на http://localhost:8000, документация на /docs)
cd backend
uv sync
uv run uvicorn app.main:app --reload

# frontend (сайт на http://localhost:5173)
cd frontend
npm install
npm run dev
```

Секреты задаются в `.env` в корне проекта.

## Тесты и линтер

Backend и бот независимы: у каждого свои зависимости и свой набор тестов. Команды запускаются из каталога соответствующего пакета.

```bash
# backend
cd backend
uv run pytest -q
uv run ruff check && uv run ruff format --check

# бот
cd bot
uv run pytest tests/ -q
uv run ruff check && uv run ruff format --check
```

Тесты backend работают с базой в памяти, тесты бота подменяют Telegram и Discord, сеть не нужна. Те же проверки (тесты и ruff) запускаются в GitHub Actions для каждого пуша и pull request.

Файлы `questions.md` и `new_questions.md` — это данные карточек, ruff их не форматирует.

## Обновление бота на сервере

```bash
git pull
docker compose build bot
docker compose up -d --no-deps bot
```

Пересоздание контейнера запускает рассылку (см. выше). Не используйте `docker compose down -v`: флаг `-v` удаляет том с базой.

Если сайт публикуется за собственным Nginx, измените порт в `docker-compose.yml` и настройте проксирование на нужный порт:

```nginx
location / {
    proxy_pass http://localhost:<порт>;
}
```

В CORS разрешены все источники, а на /api/admin/login нет ограничения числа попыток.
