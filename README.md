<div align = "center">

<img src="./static/images/logo.png"></img>

<p>Unearth Hidden Gems of Georgian Language and Culture</p>

[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)

</div>


# Description
Learn Georgian language with this django/python project.


# Test User Experience
Here are test user login credentials:
> Username: TestUserGeogem<br>
> Password: 5xPzUpKFZiQcHRa


# Installation
1. Create a virtual environment and activate it:
```
python -m venv venv
venv\scripts\activate
```
1. Install required dependencies:
```
python -m pip install -r requirements.txt
```
2. Create a `.env` file in the root directory:
```
DJANGO_SECRET_KEY='your_django_secret_key'

POSTGRES_DB='your_postgres_db_name'
POSTGRES_USER='your_postgres_db_user'
POSTGRES_PASSWORD='postgres_db_password'
POSTGRES_HOST='your_host_name (in docker it's usually the same as PG_CONTAINER_NAME)'
PG_CONTAINER_NAME='postgres_container_name'
GEOGEM_CONTAINER_NAME='site_container_name'
PGDATA='/data/geogem-postgres'

EMAIL_FROM='email_from'
EMAIL_HOST_USER='your_email_host_user'
EMAIL_HOST_PASSWORD='your_email_host_password'

RECAPTCHA_PUBLIC_KEY='your_recaptcha_public_key'
RECAPTCHA_PRIVATE_KEY='your_recaptcha_private_key'

ALLOWED_HOSTS=127.0.0.1
CSRF_TRUSTED_ORIGINS=http://127.0.0.1
DEBUG=1
```
3. Make migrations and migrate:
```
python manage.py makemigrations && python manage.py migrate
```

4. Run local server:
```
python manage.py runserver
```


## Dump database (Georgian characters)
`python -Xutf8 manage.py dumpdata > data.json` doesn't correctly encode Georgian characters in `utf-8`, so use this to dump your database:
```
python manage.py dumpdatautf8 --output data.json
```
Load the database with Georgian characters:
```
python manage.py loaddatautf8 data.json
```