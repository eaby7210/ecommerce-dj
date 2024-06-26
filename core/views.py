from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.contrib import auth
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from .permission import *
from rest_framework.permissions import IsAuthenticated
from store.serializers import CustomerSerializer,CustomerProfiledSerializer
from store.models import Customer
from allauth.account.models import EmailAddress
from django.contrib.auth.hashers import check_password
from rest_framework import status
from .serializers import *
from .models import EmailOTP
from .filter import *
from store.models import Address,Banner
User=auth.get_user_model()
# Create your views here.


      
    # send email
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
            return Response(context,template_name='authentication/signup.html',content_type='text/html')
    
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                user=serializer.user_data(request)
                user.save()
                email_otp(user)
                messages.success(request, "Account created successfully! An OTP is sent to your Email")
                return redirect("verify-email", user_id=user.id)
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
        
class VerifyEmailView(APIView):
    renderer_classes=[TemplateHTMLRenderer]

    def get(self,request,user_id=None):
        try:
            user=User.objects.only("id","email").get(pk=user_id)
        except:
            messages.warning(request,"User does not exist")
            return redirect('home')
        print("user-email",user.email)
        email=EmailAddress.objects.get(email=user.email)
        if not email.verified:
            context={
                "serializer":EmailOTPSerializer(),
                "user_id":user.id,
            }
            return Response(context,template_name="authentication/otp-confirmation.html",content_type="text/html")
        else:
            messages.info(request,"Corresponding email is already verified")
            return redirect("home")
            
    def post(self,request,user_id=None,*args,**kwargs):
        
        try:
            user=User.objects.only("id","email").get(pk=user_id)
            email=EmailAddress.objects.get(email=user.email)
        except:
            messages.warning(request,"User does not exist")
            return redirect('home')
        email_serializer=EmailOTPSerializer(data=request.data)
        try:
            email_otp=EmailOTP.objects.get(user=user)
        except:
            messages.warning(request,"OTP expired, please get a new OTP")
            return redirect("verify-email",user_id=user.id)
            
        if email_serializer.is_valid():
            otp=email_serializer.data['otp']
            if email_otp.expires_at>timezone.now():
                if otp == email_otp.otp:
                    user.is_active=True
                    email.verified=True
                    email.save()
                    user.save()
                    if request.user.is_authenticated:
                        messages.success(request,"Email verified successfully")
                        return redirect('profile')
                    else:
                        messages.success(request,"Email verified successfully you can now login again")
                        return redirect('login')
                else:
                    messages.warning(request,"Invalid OTP,Enter correct otp")
                    return redirect("verify-email",user_id=user.id)
            else:
                messages.warning(request,"OTP expired, please get a new otp")
                return redirect("verify-email",user_id=user.id)
        else:
            context={
                'user_id':user.id,
                'serializer':email_serializer
            }
            return Response(context,template_name="authentication/otp-confirmation.html",content_type="text/html") #Enter template
      

class ResendEmailView(APIView):
    renderer_classes=[TemplateHTMLRenderer]
    def send_email(self,user):
        return email_otp(user)
    def post(self,request,user_id=None):
        
        try:
            user=User.objects.get(pk=user_id)
            
        except :
            messages.warning(request,"User does not exist")
            return redirect('home')
        
        status=self.send_email(user)
        if status:
            messages.success(request, "A new OTP has been sent to your email-address")
            return Response(template_name="messages.html",content_type="text/html")
        else:
            print("error")
            messages.error(request, "An Error Occured please try again")
            return Response(template_name="messages.html",content_type="text/html")
            


       
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
        if serializer.is_valid():
            user = auth.authenticate(request, username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            # print(user.is_active,user.is_staff)
            if bool(user and user.is_staff):
                auth.login(request,user)
                messages.info(request,message='Logged in as admin succesfully')
                return redirect('dashboard')
            elif bool(user and user.is_active):
                
                auth.login(request,user)
                messages.info(request,message='Logged in succesfully')
                return redirect('/')
            elif bool(user and not user.is_active):
                messages.info(request,message='User is Blocked by Admin')
                return Response({'serializer':serializer,'error': 'User is Blocked by Admin'},template_name='authentication/login.html',content_type='text/html')
            
            else:
                messages.error(request,'Invalid credentials')
                
                return Response({'serializer':serializer,'error': 'Invalid credentials'},template_name='authentication/login.html',content_type='text/html')
        else:
            return Response({'serializer':serializer,'error': 'Invalid credentials'},template_name='authentication/login.html',content_type='text/html')
            
class LogoutAPIView(APIView):

    def get(self, request, *args, **kwargs):
        #logout
        # Remove token from the header
        auth.logout(request)
        return redirect('/')

class HomePageView(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        context = {}
        if request.user.is_authenticated:
            try:
                user = User.objects.get(username=request.user.username)
            except User.DoesNotExist:
                user = None
            
            if user is None or not user.is_active:
                request.session.flush()
            else:
                customer, created = Customer.objects.prefetch_related('user').get_or_create(user_id=user.id)
                if created:
                    messages.info(request, f"{user.username}'s profile is created as Bronze Membership")
                
                context['customer'] = customer

        # Retrieve active banners
        banners = Banner.objects.filter(is_active=True).order_by('display_order')
        context['banners'] = banners

        return Response(context, template_name='app/home.html', content_type='text/html')
    
class ProfileAPIView(APIView):
    permission_classes=[IsActive]
    renderer_classes=[TemplateHTMLRenderer]
    def get_queryset(self):
        return Customer.objects.prefetch_related('user').get(user_id=self.request.user.id)
    
    def get(self, request):
        customer=self.get_queryset()
        user=customer.user
        serializer=CustomerSerializer(customer)
        form=UserCustomerForm(instance=request.user)
        context={
            'form':form,
            'serializer':UserNormalUpdateSerializer(),
            'customer':serializer.data,
            'chgepass':ChangePasswordSerializer(),
            'member_text':customer.get_membership_display()
        }
        return Response(context,template_name="authentication/profile.html",content_type="text/html")
    def put(self,request):
        customer=self.get_queryset()
        print(request.data)
        mode=request.data.get('mode',None)
        if mode=="chnge_pass":
            data={key:value for key,value in request.data.items() if key != "mode"}
            pass_serializer=ChangePasswordSerializer(data=data,context={'request': request})
            if pass_serializer.is_valid():
                pass_serializer.save()
                auth.logout(request)
                messages.success(request,"Password is changed successfully")
                messages.info(request,"You will be redicted to login Page to login again")  
                return Response(template_name="messages.html",content_type="txt/html",status=status.HTTP_200_OK)
            else:
                messages.error(request,"Error while changing password")
                context={
                    'chgepass':pass_serializer,
                }
                print(context)
                return Response(context,template_name="app/pass-change-form.html",content_type="text/html",status=status.HTTP_400_BAD_REQUEST)
        else:           
            user_data={key: value for key, value in request.data.items()  if bool(key!="birth_date" and key!="mode")}
            customer_data = {key: value for key, value in request.data.items() if bool(key=="birth_date" and key!="mode")}
            user_serializer=UserNormalUpdateSerializer(customer.user,data=user_data,partial=True)
            customer_serializer=CustomerProfiledSerializer(customer,data=customer_data,partial=True)
            form=UserCustomerForm(request.POST,instance=request.user)
            user_is_valid = user_serializer.is_valid()
            customer_is_valid = customer_serializer.is_valid()
            if form.is_valid():
                form.save()
                # user_serializer.save()
                # customer_serializer.save()
                # customer_data=customer_serializer.data
                # customer_data['user']=user_serializer.data
                # print("cu:",customer_data)
                # # cache.invalidate_queries(Customer.objects)
                # if getattr(customer, '_prefetched_objects_cache', None):
                #     customer._prefetched_objects_cache = {}
                messages.success(request,"Profile updated successfully")
                form = UserCustomerForm(instance=request.user)
                context={
                    'form':form,
                    'chgepass':ChangePasswordSerializer(),
                    'member_text':customer.get_membership_display()
                }
                return Response(context,template_name="app/about.html",content_type="text/html")
            else:
                messages.error(request,"Please enter valid details")
                context={
                  
                    'form':form,
                    'chgepass':ChangePasswordSerializer(),
                    'member_text':customer.get_membership_display()
                }
                return Response(context,template_name="app/about.html",content_type="text/html")
    
class AddressViewSet(ModelViewSet,AdressPagination):
    permission_classes=[IsAuthenticated]
    serializer_class=AddressSerrializer
    pagination_class=AdressPagination
    renderer_classes=[TemplateHTMLRenderer]
    
    def get_template_names(self) -> list[str]:
        if self.action in ["list"]:
            return ["app/address-list.html"]
        elif self.action in ["retrive"]:
            return ["app/address.html"]
            
        return super().get_template_names()
    
    def get_customer_id(self):
        return Customer.objects.only('id').get(user_id=self.request.user.id)
    
    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'customer':self.get_customer_id()
        }
    def get_queryset(self):
        customer_id=self.get_customer_id().id
        return Address.objects.filter(customer=customer_id)
    
    def list(self, request, *args, **kwargs):
        mode=None
        if bool(request.GET):
            mode=request.GET['mode']
        if mode=="checkout-form":
            context={
                'serializer':self.get_serializer(),
                'checkout':True
            }
            return Response(context,template_name="app/address-add-form.html",content_type="text/html")
            
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        print(page)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response= self.get_paginated_response(serializer.data)
            if mode=="profile":
                return response
            elif mode=="checkout-list":
                response.template_name="app/checkout-address-list.html"
                response.content_type="text/html"
                return response
    def retrieve(self, request, *args, **kwargs):
        mode=None
        if bool(request.GET):
            mode=request.GET['mode']
        if mode=='checkout-primary':
            try:
                instance=Address.objects.get(primary=True,customer=self.get_customer_id().id)
            except Address.DoesNotExist as e:
                messages.warning(request,"There is no primary saved address in your profile,<br> Please add or select any other address")
            serializer=self.get_serializer(instance)
            context={
                'address':serializer.data
            }
            return Response(context,template_name="app/checkout-address.html",content_type="text/html")
        elif mode=="checkout-other":
            instance=Address.objects.get(id=request.GET['address'])
            serializer=self.get_serializer(instance)
            context={
                'address':serializer.data
            }
            return Response(context,template_name="app/checkout-address.html",content_type="text/html")
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        if mode=='delete':
            context={
                'address':serializer.data
            }
            return Response(context,template_name="app/address-delete.html",content_type='text/html')
        context={
            'address':serializer.data,
            'serializer':serializer
            
        }
        return Response(context,template_name="app/address-edit-form.html",content_type='text/html')
    
    def create(self, request, *args, **kwargs):
        data={key: value for key, value in request.POST.items()}
        print(data)
        mode=data.pop('mode')
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            
            instance,message,p_address,created=serializer.save()
            messages.success(request,message)
            if mode=="checkout":
                context={
                    'address':instance
                }
                return Response(context,template_name="app/checkout-address.html",content_type='text/html',status=status.HTTP_201_CREATED)
            elif mode=="address":
                return Response(
                    {'address':instance,'p_addess':p_address,'created':created},
                                template_name="app/address-items.html",content_type='text/html',
                                status=status.HTTP_201_CREATED
                                )
        else:
            messages.warning(request,"Please enter valid address data")
            return Response({'serializer':serializer},template_name="app/address-add-form.html",content_type='text/html',status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            print(serializer.validated_data)
            instance,message=serializer.update(instance,serializer.validated_data)
            messages.success(request,message)
            context={
                'serializer':serializer,
                'address':instance,
                'updated':True
            }
            return Response(
                context,
                template_name="app/address-items.html",
                content_type='text.html',
                status=status.HTTP_200_OK
             
                )
        else:
            messages.success(request,"Please enter valid Address details")
            context={
                'serializer':serializer,
                'address':instance,
                'error':True
            }
            return Response(
                context,
                template_name="app/address-edit-form.html",
                content_type='text/html'
               
                )
            
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        messages.warning(request,f"Address: {instance.name} deleted Succesfully")
        if instance.primary==True:
            address=self.get_queryset()[0]
            address.primary=True
            address.save()
            messages.info(request,f"{address.name} has set to primary address")
            return Response({'address':address},template_name='app/address-primary-update.html',content_type="text/html")
        return Response(template_name="app/nav-update.html",content_type="text/html")
    


