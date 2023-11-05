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
```
3. Make migrations and migrate:
```
python manage.py makemigrations
python manage.py migrate
```

4. Run local server:
```
python manage.py runserver
```

# Test User Experience
If you want to test out user experience, here are test user credentials:
> Username: TestUser <br>
> Password: 68ZpXQ2CqQ

# Beta version
This project is in its very early stage, so there's still lots to add, remove and update.