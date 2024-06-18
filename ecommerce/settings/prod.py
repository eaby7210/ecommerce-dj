import os
from dotenv import load_dotenv
from .common import *

load_dotenv()
DEBUG = False

ALLOWED_HOSTS = []

EMAIL_HOST = 'smtp.gmail.com' 
EMAIL_PORT = 587 
EMAIL_HOST_USER = 'eaby7210@gmail.com'  
EMAIL_HOST_PASSWORD = "iomzoayxjpqudsrz" 

SECRET_KEY =os.environ['SECRET_KEY']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'storefront',
        'HOST': 'localhost',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'port':'5432'
    }
}