<div align = "center">

<img src="./static/images/logo.png"></img>

<p>Unearth Hidden Gems of Georgian Language and Culture</p>

[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)

</div>


## Test User Experience
You can test user experience with these login credentials:

| Username | Password |
|----------|----------|
| TestUserGeogem | 5xPzUpKFZiQcHRa |


## Installation
1. Create a virtual environment and activate it:
```
python3 -m venv venv && source venv/bin/activate
```
2. Install required dependencies:
```
python3 -m pip install -r requirements.txt
```
3. Create a `.env` file in the root directory of the project:
```
DJANGO_SECRET_KEY=your_django_secret_key

SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=geogem
SQL_USER=geogem
SQL_PASSWORD=your_password
SQL_HOST=postgres
SQL_PORT=5432
PGDATA=/data/geogem-postgres
PG_CONTAINER_NAME=geogem-postgres

CELERY_BROKER=redis://redis:6379/0
CELERY_BACKEND=redis://redis:6379/0

WEB_CONTAINER_NAME=geogem
REDIS_CONTAINER_NAME=geogem-redis
CELERY_BEAT_CONTAINER_NAME=geogem-celery-beat
CELERY_WORKER_CONTAINER_NAME=geogem-celery-worker

EMAIL_FROM=example@example.com
EMAIL_HOST_USER=example@example.com
EMAIL_HOST_PASSWORD=your_password

# These are official recaptcha test keys which are used during development
RECAPTCHA_PUBLIC_KEY=6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI
RECAPTCHA_PRIVATE_KEY=6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe

ALLOWED_HOSTS=127.0.0.1 localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1 http://localhost

DEBUG=1
```
> By default, `django-admin startproject` creates an insecure `SECRET_KEY` (see [Django docs](https://docs.djangoproject.com/en/5.0/ref/checks/#:~:text=connections%20to%20HTTPS.-,security.W009,-%3A%20Your%20SECRET_KEY%20has)). Generate a secure django secret key for your project:
```
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
4. Create a Docker volume:
```
docker volume create geogem_postgres_data
```
5. Build and start Docker containers with local services:
```
sudo docker-compose up -d --build
```
> [!NOTE]  
> Celery [doesn't support](https://docs.celeryq.dev/en/stable/faq.html#does-celery-support-windows) Windows since version 4, so you can either run Celery in Docker containers (our case) or use a UNIX system to run each Celery process manually, each from a different terminal window:
```
celery -A geogem worker -l INFO
celery -A geogem beat -l INFO
```
6. Make migrations and migrate:
```
python3 manage.py makemigrations && python3 manage.py migrate
```
7. Create a super user:
```
python3 manage.py createsuperuser
```
8. Manually create a profile for the super user:
```
python3 manage.py shell

from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()
super_user = User.objects.get(is_superuser=True)
Profile.objects.create(user=super_user)

exit()
```
9. Before deploying to production, set `DEBUG` to False in `.env` by not assigning any value to DEBUG:
```
DEBUG=
```
10. Start a development web server:
```
python3 manage.py runserver
```


## Dump database (Georgian characters)
`python -Xutf8 manage.py dumpdata > data.json` doesn't correctly encode Georgian characters in `utf-8`, so use `django-dump-load-utf8` library to dump your database:
```
python3 manage.py dumpdatautf8 --output data.json
```
Load the database with Georgian characters:
```
python3 manage.py loaddatautf8 data.json
```


## Tests
> [!NOTE] 
> Before running tests, set `SQL_HOST=localhost` in `.env`

All tests are located in every app's `tests` folder.
<br>
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


## Tech Stack
The aspects of Django framework that were used during development of this project:
- Class-based views (View, DetailView, FormView, ListView, DeleteView)
- Django CustomUser, forms (UserChangeForm, UserCreationForm)
- Mixins (LoginRequiredMixin, SuccessMessageMixin)
- Internationalization (English, Russian)
- Static and media files
- ORM with PostgreSQL
- JavaScript, jQuery, Ajax requests & Chart.js
- CSS & DataTables, Bootstrap v5.3.2 (makes for a visually-appealing and mobile-friendly interface)
- django-recaptcha, email confirmation upon registration
- Docker and docker-compose.yml files
- Environment variables
- Customized admin page: SimpleListfilter, EmptyFieldListFilter
- unittests (models, views, templates and forms), coverage module
- Fixtures with test data
- Custom management commands
- Celery workers (sending activation emails in the background)
- Celery beat (deleting expired tokens at midnight)