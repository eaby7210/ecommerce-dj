# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from allauth.account.models import EmailAddress
# from .models import EmailOTP,User
# from django.core.mail import send_mail,BadHeaderError
# from django.utils import timezone
# from .serializers import generate_random_number



# @receiver(post_save, sender=User) 
# def create_token(sender, instance, created, **kwargs):
#     if created:
#         if instance.is_superuser:
#             pass

#         else:
#             otp=generate_random_number()

#             email_otp=EmailOTP.objects.create(
#                 user=instance,
#                 expires_at=timezone.now() + timezone.timedelta(minutes=5),
#                 created_at=timezone.now(),
#                 otp=otp
#                 )
#             instance.is_active=False 
#             instance.save()

#             email_otp.save()
        
#         # email credentials
        
       
#         subject="Email Verification"
#         message = f"""
#                                 Hi {instance.username}, here is your OTP {email_otp.otp},
#                                 it expires in 5 minute, use the url below to redirect back to the website.
#                                 """
#         from_email="eaby7210@gmail.com"
#         receiver = ["eabythomascu@gmail.com"]
       
#         # send email
#         try:
#             send_mail(subject,message,from_email="eaby7210@gmail.com",recipient_list=receiver,fail_silently=False)

#         except BadHeaderError as e:

#         except Exception as e:  # Catch other potential exceptions
