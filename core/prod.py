from decouple import config as cfg

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': cfg('POSTGRES_DB'),
        'USER': cfg('POSTGRES_USER'),
        'PASSWORD': cfg('POSTGRES_PASSWORD'),
        'HOST': cfg('POSTGRES_HOST'),
        'PORT': cfg('POSTGRES_PORT'),
    }
}
