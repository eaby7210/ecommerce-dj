from .common import *
from dotenv import dotenv_values


data=dotenv_values()


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1','estorefront.store']

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = data.get('SECRET_KEY')


DATABASES = {
    'default': {
        'ENGINE': data.get('DB_ENGINE'),
        'NAME': data.get('DB_NAME'),
        'HOST': data.get('DB_HOST'),
        'USER': data.get('DB_USER'),
        'PASSWORD': data.get('DB_PASSWORD'),
        'port':data.get('DB_PORT')
    }
}


EMAIL_HOST = data.get('EMAIL_HOST')
EMAIL_PORT = data.get('EMAIL_PORT')
EMAIL_HOST_USER = data.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = data.get('EMAIL_HOST_PASSWORD')

#razorpar
RAZORPAY_ID=data.get('RAZORPAY_ID')
RAZORPAY_ACCOUNT_ID=data.get('RAZORPAY_ACCOUNT_ID')