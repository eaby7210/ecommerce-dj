from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.contrib import auth
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer,HTMLFormRenderer
from .permission import *
from rest_framework_simplejwt.tokens import RefreshToken
from store.serializers import BrandDetailsSerializer,CustomerSerializer
from store.models import Brand,Customer
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
            print(context)
            for field in serializer.fields:
                print("label:",field)
                print("field:",serializer.fields[field])
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
        # print(user.is_active,user.is_staff)
        if bool(user and user.is_staff):
            auth.login(request,user)
            messages.info(request,message='Logged in as admin succesfully')
            return redirect('dashboard')
        elif bool(user and user.is_active):
            print("admin:")
            auth.login(request,user)
            messages.info(request,message='Logged in succesfully')
            return redirect('/')
        elif bool(user and not user.is_active):
            messages.info(request,message='User is Blocked by Admin')
            return Response({'serializer':serializer,'error': 'User is Blocked by Admin'},template_name='authentication/login.html',content_type='text/html')
        
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
                    messages.info(request,f"{user.username}'s profile is created as Bronze Membership")
            print("customer: ",customer.user)
            context={
                "customer":customer,
            }
            return Response(context,template_name='app/home.html',content_type='text/html')
        return Response(template_name='app/home.html',content_type='text/html')
    
class ProfileAPIView(APIView):
    permission_classes=[IsActive]
    renderer_classes=[TemplateHTMLRenderer]
    def get(self, request):
        customer=Customer.objects.prefetch_related('user').get(user_id=request.user.id)
        serializer=CustomerSerializer(customer)
        
        context={
            'serializer':serializer,
            'customer':serializer.data,
            'member_text':customer.get_membership_display()
        }
        print("context",context)
        return Response(context,template_name="authentication/profile.html",content_type="text/html")
    def post(self,request):
        pass


