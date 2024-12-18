from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CORS_ALLOW_ALL_ORIGINS = True


# from .base import *
# import os

# # SECURITY WARNING: don't run with debug turned on in production!
# #DEBUG = os.environ['DEBUG']

# DEBUG = True

# SECRET_KEY = os.environ['SECRET_KEY']

# #ALLOWED_HOSTS = ['*']
# ALLOWED_HOSTS = ['localhost']

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',  # Path to SQLite database file
#     }
# }

