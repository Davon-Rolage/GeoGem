<div align = "center">

<img src="./static/images/logo.png"></img>

<p>Unearth Hidden Gems of Georgian Language and Culture</p>

[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)

</div>


# Test User Experience
You can test user experience with these login credentials:
> Username: TestUserGeogem<br>
> Password: 5xPzUpKFZiQcHRa


# Installation
1. Create a virtual environment and activate it:
```
python -m venv venv && venv\scripts\activate
```
2. Install required dependencies:
```
python -m pip install -r requirements.txt
```
3. Create a `.env` file in the root directory of the project:
```
DJANGO_SECRET_KEY='your_django_secret_key'

POSTGRES_DB='your_postgres_db_name'
POSTGRES_USER='your_postgres_db_user'
POSTGRES_PASSWORD='postgres_db_password'
POSTGRES_HOST='localhost or the same as PG_CONTAINER_NAME'
PG_CONTAINER_NAME='postgres_container_name'
GEOGEM_CONTAINER_NAME='web_container_name'
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
4. Don't run `docker-compose up -d --build` for ***local*** development. Create a `postgres` image from `postgres_image` folder:
```
cd postgres_image && docker build -t geogem/postgres/dev .
```
5. Create a docker volume:
```
docker volume create geogem_postgres_data
```
6. Run only a `postgres` container on port `5432`:
```
docker run --name=geogem-postgres-dev -dp 5432:5432 -v geogem_postgres_data:/data/geogem-postgres -e POSTGRES_DB=your_db_name -e POSTGRES_USER=your_db_user -e POSTGRES_PASSWORD=your_db_password geogem/postgres/dev
```
7. Go back to the project's root directory, make migrations and migrate:
```
cd .. && python manage.py makemigrations && python manage.py migrate
```
8. Create a super user:
```
python manage.py createsuperuser
```
9. Run local server:
```
python manage.py runserver
```


## Dump database (Georgian characters)
`python -Xutf8 manage.py dumpdata > data.json` doesn't correctly encode Georgian characters in `utf-8`, so use `django-dump-load-utf8` library to dump your database:
```
python manage.py dumpdatautf8 --output data.json
```
Load the database with Georgian characters:
```
python manage.py loaddatautf8 data.json
```


# Tests
All tests are located in every app's `tests` folder. Current code coverage is `98%`.<br>
`coverage` tool is used for measuring code coverage. To make tests run faster, the `geogem/test_settings.py` is used which includes a more simple password hasher algorithm:
```
coverage run manage.py test --settings=geogem.test_settings
```
Get a code coverage report:
```
coverage report
```
Get annotated HTML listings with missed lines:
```
coverage html
```
Head to the created `htmlcov` folder and open `index.html` with `Live server`


# Tech Stack
The aspects of Django framework that were used during development of this project:
- Class-based views (View, DetailView, ListView, DeleteView)
- Django CustomUser, forms (UserChangeForm, UserCreationForm)
- Mixins (LoginRequiredMixin, SuccessMessageMixin)
- Internationalization (English, Russian)
- Static and media files
- ORM with PostgreSQL
- JavaScript, jQuery, Ajax requests & Chart.js
- CSS & DataTables, Bootstrap v5.3.2 (makes for a visually-appealing and mobile-friendly interface)
- django-recaptcha, email confirmation upon registration
- unittests (models, views, templates and forms), coverage module
- Docker and docker-compose.yml files
- Environment variables
- Customized admin page: SimpleListfilter, EmptyFieldListFilter