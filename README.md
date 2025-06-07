# Telegram Blog Bot

Телеграм бот для управления блогом с использованием Django и Django Ninja.

## Описание

Бот позволяет:
- Просматривать список постов
- Создавать новые посты
- Управлять постами через API
- Аутентификацию пользователей через JWT

## Технологии

- Python 3.8+
- Django 4.2+
- Django Ninja
- python-telegram-bot
- SQLite (для разработки)

## Установка

1. Клонируйте репозиторий:
```bash
git clone <url-репозитория>
cd django_tg_bot
```

2. Создайте виртуальное окружение и активируйте его:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` в корневой директории проекта:
```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

```

5. Примените миграции:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

## Запуск

1. Запустите Django сервер:
```bash
python manage.py runserver
```

2. В отдельном терминале запустите бота:
```bash
python manage.py run_bot
```

## API Endpoints

### Пользователи
- `POST /api/users/register` - Регистрация нового пользователя
- `POST /api/users/login` - Вход в систему
- `POST /api/users/refresh` - Обновление JWT токена
- `GET /api/users/me` - Получение информации о текущем пользователе

### Блог
- `GET /api/blog/posts` - Получение списка постов
- `GET /api/blog/posts/{id}` - Получение поста по ID
- `POST /api/blog/posts` - Создание нового поста
- `PUT /api/blog/posts/{id}` - Обновление поста
- `DELETE /api/blog/posts/{id}` - Удаление поста

## Команды бота

- `/start` - Начало работы с ботом
- `/posts` - Просмотр списка постов
- `/help` - Справка по командам

## Структура проекта

```
django_tg_bot/
├── tg_bot/
│   ├── blog/
│   │   ├── api.py
│   │   ├── bot.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── services.py
│   ├── users/
│   │   ├── api.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── services.py
│   └── tg_bot/
│       ├── settings.py
│       ├── urls.py
│       └── wsgi.py
├── .env
├── requirements.txt
└── manage.py
```
