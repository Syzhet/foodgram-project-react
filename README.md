![Build Status](https://github.com/Syzhet/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/syzhet/foodgram-project-react/actions/workflows/foodgram_workflow.yml)

## Стек технологий 

<div>
  <img src="https://github.com/devicons/devicon/blob/master/icons/python/python-original-wordmark.svg" title="Python" alt="Python" width="40" height="40"/>&nbsp;
  <img src="https://github.com/devicons/devicon/blob/master/icons/django/django-plain.svg" title="Django" alt="Django" width="40" height="40"/>&nbsp;
  <img src="https://github.com/devicons/devicon/blob/master/icons/docker/docker-original.svg" title="Docker" alt="Docker" width="40" height="40"/>&nbsp;
  <img src="https://github.com/devicons/devicon/blob/master/icons/github/github-original.svg" title="GitHub" alt="GitHub" width="40" height="40"/>&nbsp;
  <img src="https://github.com/devicons/devicon/blob/master/icons/nginx/nginx-original.svg"  title="nginx" alt="nginx" width="40" height="40"/>&nbsp;
</div>

## Описание проекта
Foodgram это онлайн-ресурс для публикации рецептов.
Пользователи могут создавать свои рецепты, читать рецепты других пользователей, подписываться на интересных авторов, добавлять рецепты в избранное, а также создавать список покупок и загружать его в _CSV_ формате

# Установка проекта локально
Склонировать репозиторий на локальную машину:
'''sh
git clone https://github.com/Syzhet/foodgram-project-react.git
cd foodgram-project-react
'''
Cоздать и активировать виртуальное окружение (проект разрабатывался на версии [python-3.8.2](https://www.python.org/downloads/release/python-382/)):
'''sh
python3 -m venv venv
source venv/bin/activate
'''
Cоздайте файл .env в директории с файлом age.py содержанием:
SECRET_KEY=секретный ключ django
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
Перейти в директирию и установить зависимости из файла requirements.txt:
'''sh
cd backend/foodgram/
pip install -r requirements.txt
'''
Выполните миграции:
'''sh
python manage.py migrate
'''
Запустите сервер:
'''sh
python manage.py runserver
'''

# Запуск проекта в Docker контейнере
Установите Docker и docker-compose
'''sh
sudo apt install docker.io 
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
'''
Параметры запуска описаны в файлах docker-compose.yml и nginx.conf которые находятся в директории infra/.
При необходимости добавьте/измените адреса проекта в файле nginx.conf

Запустите docker compose:
'''sh
sudo docker-compose up -d
'''

После сборки появляются 3 контейнера:

| Контайнер | Описание |
| ------ | ------ |
| db | контейнер базы данных |
| backend | контейнер приложения backend |
| nginx | контейнер web-сервера nginx |

Примените миграции:
'''sh
sudo docker-compose exec backend python manage.py migrate
'''
Загрузите ингредиенты:
'''sh
docker-compose exec backend python manage.py load_csv_ingredients
'''
Создайте администратора:
'''sh
docker-compose exec backend python manage.py createsuperuser
'''
Соберите статику:
'''sh
docker-compose exec backend python manage.py collectstatic --noinput
'''

## Адрес сайта 
http://84.201.176.57/

## Документация API
http://84.201.176.57/api/docs/

## Авторы проекта

[Ионов А.В.](https://github.com/Syzhet) - Python разработчик. Разработал backend для проекта.
[Яндекс.Практикум](https://practicum.yandex.ru/) Фронтенд для сервиса Foodgram.

