from django.contrib.auth import get_user_model
from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from rest_framework import serializers
from django.db import transaction

User=get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    
    phone = serializers.RegexField(
        regex=r'^\d{10}$', 
        error_messages={
            'invalid': 'Phone number must be 10 digits long with no spaces or hyphens.'
            }
    )
    class Meta:
        model=User
        fields=['id','first_name','last_name','username','email','phone','password1','password2']
   
    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            try:
                emails=User.objects.get(email=email)
            except:
                emails=None
            if email and bool(emails):
                raise serializers.ValidationError(
                    _('A user is already registered with this e-mail address.'),
                )
        return email


    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({'password2':"The two password fields didn't match."})
        return data

    def custom_signup(self, request, user):
        pass
    def user_data(self,request):
        user=User.objects.create_user(
            phone=self.validated_data['phone'],
            password=self.validated_data['password1'],
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            first_name=self.validated_data.get('first_name',''),
            last_name=self.validated_data.get('last_name',''),
        )
        self.custom_signup(request,user)
        setup_user_email(request, user, [])
        return user
        
    

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
        
        
class UserSerializer(serializers.ModelSerializer):
    
    class Meta():
        model=User
        fields=['id','first_name','last_name','username','email','phone']
        
