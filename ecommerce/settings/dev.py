from .common import *
from dotenv import dotenv_values
from urllib.parse import urlparse
import os


data = dotenv_values()


# SECURITY WARNING: don't run with debug turned on in production!
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "http://localhost:8000",]
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = data.get('SECRET_KEY')


# DATABASES = {
#     'default': {
#         'ENGINE': data.get('DB_ENGINE'),
#         'NAME': data.get('DB_NAME'),
#         'HOST': data.get('DB_HOST'),
#         'USER': data.get('DB_USER'),
#         'PASSWORD': data.get('DB_PASSWORD'),
#         'port': data.get('DB_PORT')
#     }
# }

tmpPostgres = urlparse(data.get("DATABASE_URL"))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': tmpPostgres.path.replace('/', ''),
        'USER': tmpPostgres.username,
        'PASSWORD': tmpPostgres.password,
        'HOST': tmpPostgres.hostname,
        'PORT': 5432,
    }
}

EMAIL_HOST = data.get('EMAIL_HOST')
EMAIL_PORT = data.get('EMAIL_PORT')
EMAIL_HOST_USER = data.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = data.get('EMAIL_HOST_PASSWORD')

# razorpar
RAZORPAY_ID = data.get('RAZORPAY_ID')
RAZORPAY_ACCOUNT_ID = data.get('RAZORPAY_ACCOUNT_ID')
