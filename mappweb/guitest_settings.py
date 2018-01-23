# Django settings for running gui tests withdjango_ecommerce project.
from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test_sh',
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

SERVER_ADDR = "127.0.0.1:9001"

mongo.connect('test_Maps', alias="test")
