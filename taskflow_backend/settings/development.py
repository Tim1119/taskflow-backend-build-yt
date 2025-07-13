from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",
]


# In your development settings (settings/development.py)
SECURE_SSL_REDIRECT = False  # Django won't redirect to HTTPS
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False