# Python Interview Cards

Сайт и бот с карточками для подготовки к Python собеседованиям.

## Стек
- **Бот**: Aiogram 
- **Backend**: FastAPI + SQLite (SQLAlchemy)
- **Frontend**: Vue 3 + Vite + Pinia + highlight.js
- **Deploy**: Docker Compose + Nginx

## Быстрый старт

```bash
cp .env.example .env

docker compose up -d --build

# 3. Импорт вопрос из questions.md
docker compose exec backend python app/scripts/migrate_md.py --file app/scripts/questions.md

# Сайт доступен на http://localhost:8080
```


## API

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/cards` | Список карточек (поиск, фильтры, пагинация) |
| GET | `/api/cards/{id}` | Одна карточка |
| GET | `/api/cards/categories` | Список категорий |
| POST | `/api/admin/login` | Получить JWT токен |
| POST | `/api/admin/cards` | Создать карточку |
| PUT | `/api/admin/cards/{id}` | Обновить карточку |
| DELETE | `/api/admin/cards/{id}` | Удалить карточку |

## Импорт questions.md

Скрипт парсит markdown файл и загружает карточки в БД.
Формат файла: заголовки H1/H2 - категории, H3+ - вопросы.

# Импорт с очисткой старых данных
```bash
docker compose exec backend python scripts/migrate_md.py --file questions.md --clear
```
или
```bash
docker compose exec -e PYTHONPATH=/app backend uv run python app/scripts/migrate_md.py --file app/scripts/questions.md --clear
```
# Импорт без очистки (добавляет к существующим)
```
docker compose exec backend python scripts/migrate_md.py --file questions.md
```

После импорта можно вручную выставить difficulty через admin UI.

## Деплой на сайт

Если уже есть Nginx на сервере изменить порт в docker-compose.yml
и настроть reverse proxy на свой домен:

```nginx
location / {
    proxy_pass http://localhost:80;
}
```

# Терминал 1 бэкенд
cd backend
uv sync
uv run uvicorn app.main:app --reload
# API http://localhost:8000
# Документация: http://localhost:8000/docs

# Терминал 2 фронтенд
cd frontend
npm install
npm run dev
# Сайт http://localhost:5173

docker compose exec backend python app/scripts/migrate_md.py --file app/scripts/questions.md
docker compose exec -e PYTHONPATH=/app backend uv run python app/scripts/migrate_md.py --file app/scripts/questions.md

docker compose up -d --build

docker compose logs -f

docker compose logs -f bot
docker compose logs -f backend
