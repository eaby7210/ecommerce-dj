from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.contrib import auth
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
# from django.conf import settings
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from rest_framework_simplejwt.tokens import RefreshToken
from store.serializers import CollectionDetailsSerializer
from store.models import Collection,Customer
from django.db.models.aggregates import Count
from rest_framework import status
from .serializers import *

# user=settings.AUTH_USER_MODEL
# Create your views here.

class SignupAPIView(APIView):
    renderer_classes=[TemplateHTMLRenderer]
    def get(self, request):
        if request.user.is_authenticated:
            messages.info(request,"Already Signed in")
            return redirect('/')
        else:
            serializer=RegisterSerializer()
            context={
                "serializer":serializer
            }
            return Response(context,template_name='authentication/signup.html',content_type='text/html')
    
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                user=serializer.user_data(request)
                user.save()
                authuser=auth.authenticate(request,username=serializer.validated_data["username"],password=serializer.validated_data["password1"])
            
            
            if bool(user) and bool(authuser):
                # refreshtoken=RefreshToken.for_user(user)
                # request.session['rtoken']=refreshtoken
                auth.login(request,authuser)
                messages.success(request,'Registration succesfull')
                return redirect('home')
            elif bool(user):
                messages.error(request,'Error while authentication, try login again')
                return Response({'serializer':serializer},template_name='authentication/signup.html',content_type='text/html')
        else:
            context={
                'serializer':serializer
            }
            return Response(context,template_name='authentication/signup.html',content_type='text/html')
       
class LoginAPIView(APIView):
    renderer_classes=[TemplateHTMLRenderer]
    permission_classes=[AllowAny]
    
    def get(self, request):
        if request.user.is_authenticated:
            messages.info(request,'Already LogedIn')
            return redirect('/')
        else:
            serializer=UserLoginSerializer()
            return Response({'serializer':serializer},template_name='authentication/login.html',content_type='text/html')
        
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = auth.authenticate(request, username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        if user is not None:
            print(user)
            auth.login(request,user)
            messages.info(request,message='Logged in succesfully')
            return redirect('/')
        else:
            messages.error(request,'Invalid credentials')
            
            return Response({'serializer':serializer,'error': 'Invalid credentials'},template_name='authentication/login.html',content_type='text/html')

class LogoutAPIView(APIView):

    def get(self, request, *args, **kwargs):
        #logout
        # Remove token from the header
        auth.logout(request)
        return redirect('/')

class HomePageView(APIView):
    renderer_classes=[TemplateHTMLRenderer]
    def get(self, request):
        if request.user.is_authenticated:
            try:
                user=User.objects.get(username=request.user.username)
            except User.DoesNotExist:
                user=None
            if user is None or user.is_active is False:
                request.session.flush()
            else:
                customer,created=Customer.objects.prefetch_related('user').get_or_create(user_id=user.id)
                if created:
                    messages.info(f"{user.username}'s profile is created as Bronze Membership")
            print("customer: ",customer.membership)
            context={
                "customer":customer,
            }
            return Response(context,template_name='app/home.html',content_type='text/html')
        return Response(template_name='app/home.html',content_type='text/html')


# @api_view(['GET'])
# def home(request):
#     user_data="User is not authenticated."
#     collections = Collection.objects.annotate(products_count=Count('products')).all()
#     collection_serializer = CollectionDetailsSerializer(collections,many=True)
#     response_data = {
#         'collections': collection_serializer.data,
#         'users': user_data
#     }
#     if request.user.is_authenticated:
        
#         user_data=UserSerializer(request.user)
#         response_data = {
#         'collections': collection_serializer.data,
#         'users': user_data.data
#     }
#         return Response(response_data)
        
        
    
#     return Response(response_data)
# @api_view(['GET','POST'])
# def signup(request):
#     if request.method=='POST':
#         serializer=UserRegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response("ok",status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
#     elif request.method=='GET':
#         return Response("ok")
        



# def signup(request):
#     if request.method=='POST':
#         fname=request.POST['firstName'].strip()
#         lname=request.POST['lastName'].strip()
#         username=request.POST['userName'].strip()
#         email=request.POST['email'].strip()
#         pass1=request.POST['password'].strip()
#         pass2=request.POST['confirmPassword'].strip()
#         print((fname,lname,username,email,pass1,pass2))
#         check=any(not field for field in (fname, lname, username, email, pass1, pass2))
#         print(check)
#         if check:
#             messages.info(request,'All feilds must be filled correctly')
#             return render(request,'authentication/signup.html')
            
#         else:
#             if pass1==pass2:
#                 if User.objects.filter(username=username).exists():
#                     messages.info(request,'Username already taken')
#                     return render(request,'authentication/signup.html')
#                 elif User.objects.filter(email=email).exists():
#                     messages.info(request,'Email is already taken')
#                     return render(request,'authentication/signup.html')
#                 else:
#                     user=User.objects.create_user(
#                         first_name=fname,
#                         last_name=lname,
#                         username=username,
#                         email=email,
#                         password=pass1,   
#                     )
#                     user.save()
#                     user=auth.authenticate(username=username,password=pass1)
#                     if user is not None:
#                         request.session['user_var']=username
#                         auth.login(request,user)
#                         messages.success(request,'Registration succesfull')
#                         return redirect('/')
#                     else:
#                         messages.error(request,'Error while authenticate, try login again')
#                         return render(request,'authentication/login.html')
                    
#             else:
#                 messages.info(request,'password do not match')
#                 return render(request,'authentication/signup.html')
            
        
    
    
#     else:
#         if request.user.is_authenticated:
#             messages.info(request,"Logout to signup")
#             return redirect('/')
#         else:
#             return render(request,'authentication/signup.html')



# def login(request):
#     if request.method=='POST':
#         username=request.POST['username'].strip()
#         password=request.POST['password'].strip()
#         if username=='' or password=='':
#             messages.info(request,'All feild must be filled')
#             return render(request,'authentication/login.html')
#         else:
#             user=auth.authenticate(username=username,password=password)
#             if user is not None:
#                 auth.login(request,user)
#                 request.session['user_var']=username
#                 response=redirect('/')
#                 response.set_cookie('user_cookie',username,max_age=3600)
#                 return response
#             else:
#                 messages.info(request,'Invalid username or password')
#                 return render(request,'authentication/login.html')
#     else:
#         if request.user.is_authenticated:
#             messages.info(request,"Logout to Login")
#             return redirect('/')
#         else:
#             return render(request,'authentication/login.html')
    
# def logout(request):
#     if 'user_var' in request.session:
#         del request.session['user_var']
#     response=redirect('/')
#     response.delete_cookie('user_cookie')
#     auth.logout(request)
#     return response
