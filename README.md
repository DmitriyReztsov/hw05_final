# Yatube project
Yatube

# Yatube

Социальная сеть с реализацией возможности публиковать посты с изображениями, подписываться на авторов, получать список постов избранных авторов. Реализован бэкенд на Django. Фронт взят из стандартной библиотеки.

## Tech

- Python
- Django
- SQLite3
- HTML

## Installation

Выполните установку зависимостей:
```sh
pip instal -r requirements.txt
```
Выполните миграции:
```sh
python manage.py makemigrations
python manage.py migrate
```
Создайте суперпользователя и запустите сервер:
```sh
python manage.py createsuperuser
python manage.py runserver
```
Сервер запускается локально на IP http://127.0.0.1:8000/


## Author

Dmitriy Reztsov
