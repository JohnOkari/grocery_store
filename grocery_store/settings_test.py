from .settings import *  # noqa

# Use fast, ephemeral SQLite database for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# In-memory email backend for assertions
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

ALLOWED_HOSTS = ['*']

# Ensure deterministic secret
SECRET_KEY = 'test-secret-key'

# Default test phone to ensure SMS path executes when needed
TEST_CUSTOMER_PHONE = '0712345678'


