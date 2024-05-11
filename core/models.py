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
    
class EmailOTP(models.Model):
    created_at=models.DateTimeField(auto_now_add=True)
    expires_at=models.DateTimeField(blank=True,null=True)
    otp=models.CharField(max_length=6)
    user=models.ForeignKey(User, on_delete=models.CASCADE,related_name='otp_users')
    
    def __str__(self):
        return self.user.username
    
        
