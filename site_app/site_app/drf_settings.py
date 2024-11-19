from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'user_id',  # Tell SIMPLE_JWT to use 'user_id' as the primary key
    'USER_ID_CLAIM': 'user_id', 
}


import os

if os.getenv('USE_DRF_SETTINGS', 'True') == 'True':
    from .drf_settings import REST_FRAMEWORK, SIMPLE_JWT
