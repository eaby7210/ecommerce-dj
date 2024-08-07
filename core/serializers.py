from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from django.core.mail import send_mail,BadHeaderError
from django.utils import timezone
from django.contrib import messages
from .models import EmailOTP
from store.models import Address,Customer
from rest_framework import serializers
from django.db import transaction
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError
import random
from datetime import date



User=get_user_model()

def sends_mail(user,otp):
    subject="Email Verification"
    message = f"""
            Hi {user.first_name} {user.last_name},
            here is your OTP {otp} for confirming your email,
            current otp will expires in 5 minute.
            """
    from_email="eaby7210@gmail.com"
    receiver = ["eabythomascu@gmail.com",user.email]
    try:
        send_mail(subject,message,from_email=from_email,recipient_list=receiver,fail_silently=False)
       
        return True
    except BadHeaderError as e:
    
        return False
    except Exception as e:  # Catch other potential exceptions
      
        return False
    
def email_otp(user):
    if user.is_superuser:
      
        return False

    else:
        otp=generate_random_number()
        try:
            email_otp=EmailOTP.objects.get(user=user)
            
            email_otp.otp=otp
            email_otp.expires_at=timezone.now()+timezone.timedelta(minutes=5)
            email_otp.save()
          
        except EmailOTP.DoesNotExist as e:
          
            email_otp=EmailOTP.objects.create(
                user=user,
                otp=otp,
                expires_at=timezone.now() + timezone.timedelta(minutes=5),
                created_at=timezone.now(),
                )
      
            email_otp.save()
        
        status=sends_mail(user,otp)
       
        if status:
            return True
        else:
            return False

def generate_random_number():
  """Generates a random 6-digit integer."""
  return random.randint(100000, 999999)


class UserCustomerForm(forms.ModelForm):
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Select a date',
                'type': 'date',  # HTML5 date input type
            }
        )
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'birth_date']
        
    def __init__(self, *args, **kwargs):
        super(UserCustomerForm, self).__init__(*args, **kwargs)
        # Include the birth_date field from the Customer model
        if self.instance and hasattr(self.instance, 'user'):
            self.fields['birth_date'].initial = self.instance.user.birth_date
            
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > date.today():
            raise ValidationError("Birth date cannot be in the future.")
        return birth_date
        
    def save(self, commit=True):
        user = super(UserCustomerForm, self).save(commit=False)
        if commit:
            user.save()
            # Save the Customer birth_date separately
            if hasattr(user, 'user'):
                user.user.birth_date = self.cleaned_data['birth_date']
                user.user.save()
        return user

class EmailOTPSerializer(serializers.ModelSerializer):
    otp=serializers.CharField(
        validators=[
            RegexValidator(
        regex=r'^\d{6}$',
        message="OTP must be 6 numeric digit",
        code="invalid"
    )]
    )
    class Meta:
        model=EmailOTP
        fields=['otp']

class ChangePasswordSerializer(serializers.Serializer):
    old_password=serializers.CharField(required=True,style={'input_type': 'password'},write_only=True)
    new_password=serializers.CharField(required=True,style={'input_type': 'password'},write_only=True)
    confirm_password=serializers.CharField(required=True,style={'input_type': 'password'},write_only=True)
    
    def validate_new_password(self,value):
        validate_password(value)
        return value
    
    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            messages.warning(self.context['request'],"Old password is incorrect")
            raise serializers.ValidationError(_("Old password is incorrect"))
        if attrs['new_password'] == attrs['old_password']:
            messages.warning(self.context['request'],"Old password and New password are the same.")
            raise serializers.ValidationError({"confirm_password": _("Old password and New password are the same.")})
    
        if attrs['new_password'] != attrs['confirm_password']:
            messages.warning(self.context['request'],"The new password fields didn't match.")
            raise serializers.ValidationError({"confirm_password": _("The new password fields didn't match.")})
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
        

    

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    phone=forms.CharField(label="Phone no.",validators=[
        RegexValidator(
        regex=r'^\d{10}$',
        message="Phone number must be 10 digits long with no spaces or hyphens.",
        code="invalid"
    )])
    email=forms.EmailField(label="E-mail",required=allauth_settings.EMAIL_REQUIRED)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'password1', 'password2']
        widgets={
            'username':forms.TextInput(attrs={"hx-post":""})
        }
        help_texts={
            'username':''
            
        }


    def clean_username(self):
        username = self.cleaned_data['username']
        return get_adapter().clean_username(username)

    def clean_email(self):
        email = self.cleaned_data['email']
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            try:
                User.objects.get(email=email)
                raise forms.ValidationError(_('A user is already registered with this e-mail address.'))
            except User.DoesNotExist:
                pass
        return email

    def clean(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError({'password2': "The two password fields didn't match."})
        return self.cleaned_data

    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            self.custom_signup(self.request, user)  # Assuming you have a custom signup method
            setup_user_email(self.request, user, [])  # Assuming you have a setup_user_email function
        return user

class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(style={'input_type': 'password'},write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'},write_only=True)
    
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
                    ('A user is already registered with this e-mail address.'),
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
    password = serializers.CharField(style={'input_type': 'password'},write_only=True)
              
class UserSerializer(serializers.ModelSerializer):
    password=serializers.CharField(style={'input_type': 'password'},write_only=True)
    class Meta():
        model=User
        fields=['id','first_name','last_name','username','email','phone','is_active','is_staff','password']

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta():
        model=User
        fields=['id','first_name','last_name','username','email','phone','is_active','is_staff']

class UserNormalUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)
    phone = serializers.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Phone number must be 10 digits long with no spaces or hyphens.'
            )
        ]
    )
        
class AddressSerrializer(serializers.ModelSerializer):
   
    class Meta():
        model=Address
        fields=['id','name','state','city','pin','primary','other_details']
    def update(self, instance, validated_data):
        customer=self.context['customer']
        instance.name = validated_data.get('name', instance.name)
        instance.state = validated_data.get('state', instance.state)
        instance.city = validated_data.get('city', instance.city)
        instance.pin = validated_data.get('pin', instance.pin)
        instance.primary = validated_data.get('primary', instance.primary)
        instance.other_details = validated_data.get('other_details', instance.other_details)
        if instance.primary:
            ol_address=Address.objects.filter(customer=customer,primary=True)
            for item in ol_address:
                item.primary=False
                item.save()
        instance.save()
        message=f'You address {instance.name} is updated successfully'
        return instance,message
    def save(self, **kwargs):
        customer=self.context['customer']
        validated_data = {**self.validated_data}
        validated_data['customer']=customer
   
        primary=validated_data.get('primary',False)
        if primary:
            ol_address=Address.objects.filter(customer=customer,primary=True)
            for item in ol_address:
                item.primary=False
                item.save()

        address,created=Address.objects.get_or_create(**validated_data)
        if created:
            message=f'You new address {address.name} saved successfully'
            address.save()
        else:
            message=f'You address {address.name} is updated successfully'
            address.save()
        if primary:
            return address,message,ol_address,created
        else:
            return address,message,None,created