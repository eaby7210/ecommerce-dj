import pprint
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
# from django.core.cache import cache
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import TemplateHTMLRenderer
from django.db.models.aggregates import Count
from store.models import *
from store.serializers import *
from .filter import *
from core.serializers import UserUpdateSerializer
from rest_framework.response import Response
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAdminUser

User=get_user_model()



# Create your views here.

class Dashboard(APIView):
    renderer_classes=[TemplateHTMLRenderer]
    permission_classes=[IsAdminUser]
    def get(self,request):
        context={}
        return Response(context,template_name='admin/dashboard.html',content_type='text/html')
        

class UserViewSet(ModelViewSet):
    queryset=Customer.objects.select_related('user').all()
    serializer_class=CustomerSerializer
    filter_backends=[DjangoFilterBackend]
    filterset_fields=[]
    renderer_classes=[TemplateHTMLRenderer]
    pagination_class=PageNumberPagination
    permission_classes=[IsAdminUser]
    
    def get_template_names(self) -> list[str]:
        if self.action in ['update','retrieve']:
            return ['admin/customer_edit.html']
        return ['admin/customers.html']
    
    def get_serializer_context(self):
        return super().get_serializer_context()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user_data={key.split(".")[1]: value for key, value in request.data.items()  if key.startswith("user.")}
        customer_data = {key: value for key, value in request.data.items() if not key.startswith("user.")}
        if not 'is_active' in user_data:
            user_data['is_active']=False
        if not 'is_staff' in user_data:
            user_data['is_staff']=False
        # print("\nuser: ",user_data,"\ncustomer: ",customer_data)
        user_serializer=UserUpdateSerializer(instance.user,data=user_data,partial=True)
        if user_serializer.is_valid():
            serializer=CustomerUpdateSerializer(instance,data=customer_data,partial=True)
            if serializer.is_valid():
                user_serializer.save()
                serializer.save()
                customer_data['user']=user_serializer.data
                # cache.invalidate_queries(Customer.objects)
                if getattr(instance, '_prefetched_objects_cache', None):
                    instance._prefetched_objects_cache = {}
                if getattr(instance.user, '_prefetched_objects_cache', None):
                    instance.user._prefetched_objects_cache = {}
                messages.success(request,"User profile updated successfully")
                return HttpResponse("success",status=200)
            else:
                # print("cutomer-error: ",serializer.errors,)
                
                return HttpResponse(serializer.errors,status=406)
        else:
            return HttpResponse(user_serializer.errors,status=406)
        

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            messages.success(request,f"User details added successfully")
            return redirect('admin-users-list')
        else:
            errors=[f"{field} =>{error[0]}" for field,error in serializer.errors.items()]
            print(errors)
            for error in errors:
                messages.error(request,error)
            return redirect('admin-users-list')
            
     
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CustomerUpdateSerializer(instance)
        context={
            'serializer':serializer,
            'user':serializer.data   
        }
        # print(serializer.data)
        return Response(context,status=status.HTTP_200_OK)
    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.queryset, many=True)
        context={
            'users': serializer.data,
            'serializer':UserSerializer()
        }
        print(serializer.data)
        response=Response(context, status=status.HTTP_200_OK)
        response['Cache-Control'] = 'no-cache'
        return response


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_class = ProductFilter
    pagination_class = ProductPagination
    permission_classes = [IsAdminUser]
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']
    renderer_classes=[TemplateHTMLRenderer]
    

    def get_serializer(self, *args, **kwargs):
        serializer_class=None
        if self.action in ['list']:
            serializer_class=ProductSerializer
        else:
            serializer_class=ProductAdminSerializer
            
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)
    
    def get_template_names(self) -> list[str]:
         if self.action in ['retrieve']: 
             return ["admin/product_edit.html"]
         else:
             return ["admin/products_add.html"]
   
    def get_serializer_context(self):
        return {'request':self.request}
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        print(serializer.data)
        context={
            'serializer':serializer,
            'product':serializer.data
            
        }
        return Response(context,status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        print(request.data)
        print(instance.id)
        serializer=ProductAdminSerializer(instance,data=request.data,partial=True)
        if serializer.is_valid():
            print(serializer.validated_data)
            if not 'active' in serializer.validated_data:
                serializer.validated_data['active']=False
            serializer.save()
            
            messages.success(request,"Product updated successfully")
            return HttpResponse("success",status=200)
        else:
            print("cutomer-error: ",serializer.errors,)
            return HttpResponse(serializer.errors,status=406)
 
    def create(self, request, *args, **kwargs):
        serializer = ProductAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        messages.success(request,"Product created successfully")
        return redirect('admin-product-list')
    
    def destroy(self,request,*args, **kwargs):
        # product=get_object_or_404(Product,pk=pk)
        # if product.orderitems.count()>0:
        if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
            return Response({'error':'Product cannot be deleted Since there are orders assossiated with this product'})
        instance = self.get_object()
        self.perform_destroy(instance)
        return redirect('admin-product-list')
    

class CategoryAdminViewSet(ModelViewSet):
    queryset=Main_Category.objects.annotate(products_count=Count('categories_products')).all()
    pagination_class=CategoryPagination
    serializer_class=CategoryAdminSerializer
    permission_classes=[IsAdminUser]
    renderer_classes=[TemplateHTMLRenderer]
    
    def get_template_names(self) -> list[str]:
        if self.action == 'retrieve':
            return ["admin/category.html"]
        return ["admin/categories-list.html"]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            messages.success(request,"Category added successfully")
            return redirect('main_category-list')
        else:
            errors=[f"{field} =>{error[0]}" for field,error in serializer.errors.items()]
            print(errors)
            for error in errors:
                messages.error(request,error)
            return redirect('main_category-list')
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        print(request.data)
        print(instance.id)
        serializer=CategoryAdminSerializer(instance,data=request.data,partial=True)
        if serializer.is_valid():
            print(serializer.validated_data)
            if not 'active' in serializer.validated_data:
                serializer.validated_data['active']=False
            serializer.save()
            
            messages.success(request,"Category updated successfully")
            return HttpResponse("success",status=200)
        else:
            print("cutomer-error: ",serializer.errors,)
            return HttpResponse(serializer.errors,status=406)
        
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CategoryAdminSerializer(instance)
        print(serializer.data)
        context={
            'serializer':serializer,
            'category':serializer.data
            
        }
        return Response(context,status=status.HTTP_200_OK)
    
    def get_serializer_context(self):
        return {'request':self.request}

class BrandViewSet(ModelViewSet):
    queryset=Brand.objects.annotate(
        products_count=Count('brand_products')
        ).all()
    permission_classes=[IsAdminUser]
    pagination_class=BrandPagination
    serializer_class=BrandDetailsSerializer
    renderer_classes=[TemplateHTMLRenderer]
    
    
    
    def get_list(self):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
    
    
    def get_template_names(self) -> list[str]:
        if self.action in ['create','destroy']:
            return ["admin/brand-list.html"]
        elif self.action in ['list']:
            return ["admin/brand.html"]
        elif self.action in ['retrieve','update']:
            return ['admin/brand-edit.html']
            
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        context=self.get_list()
        if serializer.is_valid():
            self.perform_create(serializer)
            messages.success(request,"Brand created successfully")
            return Response(context)
        else:
            context['serializer']=serializer
            context['error']=True
            messages.error(request,"Error in Brand creation")
            return Response(context)
            # return render(request,template_name="admin/brand-list.html",context=context)
            
            
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        context={
                'serializer':serializer,
                'brand':serializer.data
            }
        return Response(context)
    def list(self, request, *args, **kwargs):
        context=self.get_list()
        print(context)
        return Response(context)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            messages.success(request,"Brand updated succesfully")
            return HttpResponse("success",status=200)
        else:
            context={
                'serializer':serializer
            }
            return HttpResponse(serializer.errors,status=406)
            
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance.active)
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    

class ProductImageViewSet(ModelViewSet,PageNumberPagination):
    serializer_class = ProductImageSerializer
    permission_classes=[IsAdminUser]
    # pagination_class=ProductImagePagination
    renderer_classes=[TemplateHTMLRenderer]
    

    def get_template_names(self) -> list[str]:
        if self.action == 'retrieve':
            return ["admin/product_image.html"]
        return ["admin/product_image-list.html"]
    
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # total_products=page.paginator.count
        # total_pages=total_products//page_size
        # if total_products % page_size != 0:
        #     total_pages += 1
        context={
            'serializer':self.get_serializer(),
            'product_id':self.kwargs['product_pk'],
            'results': serializer.data,
        }
        return Response(context)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return redirect(reverse('product_images-list',kwargs={'product_pk':self.kwargs['product_pk']}))
        else:
            pprint.pprint(serializer.errors)
            return HttpResponse("error")
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProductImageSerializer(instance)
        print(serializer.data)
        context={
            'serializer':serializer,
            'image':serializer.data,
            'product_id':self.kwargs['product_pk'],
            
        }
        pprint.pprint(context)
        return Response(context,status=status.HTTP_200_OK)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        print(request.data)
        print(instance.id)
        serializer=ProductImageSerializer(instance,data=request.data,partial=True)
        if serializer.is_valid():
            print(serializer.validated_data)
            serializer.save()
            
            messages.success(request,"Product image updated successfully")
            return HttpResponse("success",status=200)
        else:
            print("cutomer-error: ",serializer.errors,)
            return HttpResponse(serializer.errors,status=406)


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'put', 'head', 'options']
    permission_classes=[IsAdminUser]
    renderer_classes=[TemplateHTMLRenderer]
    pagination_class=PageNumberPagination
    queryset=Order.objects.select_related('customer','address','applied_coupon').prefetch_related('items').all()
    
    
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return UpdateAdminOrderSerializer
        return OrderSerializer


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.template_name="admin/order.html"
            response.content_type="text/html"
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    def update(self, request, *args, **kwargs):
        order_id=kwargs.get('pk')
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            order= Order.objects.get(id=order_id)
            if instance.order_status=='RR' and order.order_status=='RA':
                try:
                    wallet=Wallet.objects.get(customer=self.get_customer_id())
                    wallet.balance+=instance.grand_total
                    wallet.save()
                except Wallet.DoesNotExist:
                    wallet=Wallet.objects.create(
                        customer=order.customer,
                        wallet=instance.grand_total
                    )
            context={
                'order':order
            }
            return Response(context,template_name="admin/order-row.html",content_type="text/html")
    def retrieve(self, request, *args, **kwargs):
        mode=None
        if bool(request.GET):
            print(request.GET)
            mode=request.GET['mode']
        instance = self.get_object()
        
        context={
            'serializer':UpdateAdminOrderSerializer(),
            'order':instance.id
        }
        response = Response(context)
        if mode == "update":
            response.template_name="admin/order-form.html"
            response.content_type="text/html"
            return response
        else:
            serializer = self.get_serializer(instance)
            context={
                'order':serializer.data,
            }
            print(context)
            response = Response(context)
            response.template_name='admin/order-detail.html'
            response.content_type='text/html'
            return response

    
class CouponViewSet(ModelViewSet):
    permission_classes=[IsAdminUser]
    renderer_classes=[TemplateHTMLRenderer]
    pagination_class=PageNumberPagination
    serializer_class=CouponCUSerializer
    queryset=Coupon.objects.all()
    

        
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response= self.get_paginated_response(serializer.data)
            response.data['serializer']=CouponCUSerializer()
            response.template_name="admin/coupon-list.html"
            response.content_type="text/html"
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'coupon':serializer.data,
            'serializer':serializer
            },template_name="admin/coupon-edit.html",content_type="text/html")
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            messages.success(request,"Coupon saved Successfully")
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    'coupon':serializer.data,
                    'serializer':CouponCUSerializer()
                    },
                template_name="admin/coupon-row.html",
                content_type="text/html",
                status=status.HTTP_201_CREATED,
                headers=headers
                )
        else:
            context={
                'serializer':serializer
            }
            messages.error(request,"Please enter a valid Coupon details")
            return Response(context,template_name="admin/coupon-add-form.html",content_type='text/html')
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            messages.success(request,f"Coupoun {instance.id} Updated Successfully")
            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}
            context={
                'coupon':self.get_object(),
                
            }
            return Response(context,template_name="admin/coupon-row.html",content_type="text/html")
        else:
            messages.error(request,"Please enter a valid Coupon details")
            context={
                'coupon':instance,
                
            }
            return Response(context,template_name="admin/coupon-row.html",content_type="text/html")
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
class NavUpdateView(APIView):
    permission_classes=[IsAdminUser]
    renderer_classes=[TemplateHTMLRenderer]
    
    def get(self,request):
        return Response(template_name="admin/admin-nav-update.html",content_type="txt/html")
    
    
