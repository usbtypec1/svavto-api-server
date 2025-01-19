# API Server

---

## Запуск проекта:

1. Создать `.env` файл в корне проекта. Заполнить следующие поля:
2. Заполнить следующие поля:
   1. `DEBUG` - true/false - режим отладки.
   2. `ALLOWED_HOSTS` - разрешенные хосты. Для отладки можно выставить "*".
   3. `CELERY_BROKER_URL` - обычно используется redis. Выставьте redis://localhost:6379/0.
   4. `SECRET_KEY` - любая секретная строка. Можно например сгенерировать в генераторе паролей.
   5. `TELEGRAM_BOT_TOKEN` - токен бота.
3. Создать виртуальное окружение: `python3 -m venv venv`.
4. Запустить виртуальное окружение: `. venv/bin/activate`.
5. Установить зависимости: `pip install -r requirements.txt`.
6. Запустить миграции БД: `python3 manage.py migrate`.
7. Добавить цены по умолчанию: `python3 manage.py init_staff_service_prices`.
8. Добавить админа в админку Django: `python3 manage.py createsuperuser`.
9. Установить WSGI-сервер: `pip install gunicorn`.
10. Запустить проект: `gunicorn carsharing.wsgi --bind 127.0.0.1:8000`
