from .base import *

DEBUG = False

schema = os.environ.get('DB_SCHEMA', "public")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'OPTIONS': {
            'options': f"-c search_path={os.getenv('DB_SCHEMA', 'public')}",
        },
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Reutilización de conexiones
    }
}

CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "False").lower() in ("true", "1", "t", "yes")


# from .base import *
# import os

# # SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = os.environ['DEBUG']

# ALLOWED_HOSTS = ['*']

# schema = os.environ.get('DB_SCHEMA', "public")


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'OPTIONS': {
#              'options': f'-c search_path={schema}'  # Usar un schema diferente
#          },
#         'NAME': os.environ['DB_NAME'],  # Base de datos de desarrollo
#         'USER': os.environ['DB_USER'],
#         'PASSWORD': os.environ['DATABASE_PASSWORD'],
#         'HOST': os.environ['DB_HOST'],
#         'PORT': int(os.environ['DB_PORT']),
#         'CONN_MAX_AGE': 0,  # Deshabilita conexiones persistentes
        
#     }
# }
