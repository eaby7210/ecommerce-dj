from .common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-qy+vs#(+2%9$d@_q#hc2n0+u18kxmg24ax-!7jz+w^%qvz^nsl'


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


EMAIL_HOST = 'smtp.gmail.com' 
EMAIL_PORT = 587 
EMAIL_HOST_USER = 'eaby7210@gmail.com'  
EMAIL_HOST_PASSWORD = "iomzoayxjpqudsrz" 

#razorpar
RAZORPAY_ID='rzp_test_XqEMlS82BGA5ki'
RAZORPAY_ACCOUNT_ID='mDSlw9kn3UIrTNZLe6rk3HJh'