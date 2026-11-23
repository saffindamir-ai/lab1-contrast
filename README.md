# ЛР № 1. Веб-приложение «Изменение контраста изображения» (вариант 2)

Flask-приложение: загрузка картинки, выбор уровня контраста (0–3),
проверка Google reCAPTCHA v2, вывод исходной и полученной картинок
и графиков распределения цветов R, G, B.

## Запуск локально
```bash
pipenv install                 # установка зависимостей из Pipfile
export RECAPTCHA_PUBLIC_KEY=... # ключи из https://www.google.com/recaptcha/admin
export RECAPTCHA_PRIVATE_KEY=...
export SECRET_KEY=любая_случайная_строка
pipenv run gunicorn --bind 127.0.0.1:5000 wsgi:app
```
Открыть http://127.0.0.1:5000/contrast

## Тесты
```bash
pipenv run python -m pytest -v my_tests.py
```

## Деплой на render.com
- Build Command: `python -m pip install pipenv && pipenv sync`
- Start Command: `pipenv run gunicorn wsgi:app --bind 0.0.0.0:$PORT`
- Environment: `PYTHON_VERSION=3.11.9`, `SECRET_KEY`, `RECAPTCHA_PUBLIC_KEY`, `RECAPTCHA_PRIVATE_KEY`
