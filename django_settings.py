import uuid


SECRET_KEY = uuid.uuid4()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'travis_ci_db',
        'USER': 'travis',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
    }
}

MIDDLEWARE_CLASSES = ()

INSTALLED_APPS = (
    'test_models',
)
