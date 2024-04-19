from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Create your models here.
class User(AbstractUser):
    phone = models.CharField(max_length=10,
        validators=
        [
            RegexValidator(
                regex=r'^\d{10}$',
                message='Phone number must be 10 digits long with no spaces or hyphens.'
                )
        ]
    )
    email=models.EmailField(unique=True, max_length=254)
    active=models.BooleanField(default=False)
    
