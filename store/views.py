from django.http import HttpResponse,JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models.aggregates import Count
from django.db.models import Prefetch
from .models import Product,Brand,Address
from .serializers import *
from .filter import ProductPagination,ProductFirstPagination
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import *
from rest_framework.viewsets import ModelViewSet, GenericViewSet,ReadOnlyModelViewSet
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status
# import pprint
#from rest_framework.response import SimpleTemplateResponse
#from rest_framework.mixins.

# Create your views here.

class ProductListView(APIView, PageNumberPagination):
    """
    API view to get a paginated list of active products with HTML template rendering.
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'app/products.html'  # Assuming template location
    page_size=20
    # filterset_class = ProductFilter
    def get(self, request, format=None):
        """
        Get a list of active products.
        """
        if request.user.is_authenticated:
            customer = Customer.objects.get(user=self.request.user)
            queryset=Product.objects.prefetch_related(
                'images',
                Prefetch(
                    'cartitem_set',queryset=CartItem.objects.only('id','quantity').filter(customer=customer),
                         to_attr='cart_items'
                         )
                ).select_related('brand', 'category').filter(active=True)
        else:
            queryset = Product.objects.prefetch_related('images').select_related('brand').select_related('category').filter(active=True)
        page = self.paginate_queryset(queryset,request)
        if page is not None:
            if request.user.is_authenticated:
                serializer=ProductCartSerializer(page, many=True, context={'request': request})
            else:
                serializer = ProductSerializer(page, many=True, context={'request': request})
            # print("data : ",serializer.data)
            total_products=self.page.paginator.count
            page_size=self.get_page_size(request)
            total_pages=total_products//page_size
            if total_products % page_size != 0:
                total_pages += 1
            
            context={
                'total_pages':total_pages,
                'page_number':self.get_page_number(request,paginator=page),
                'page_size':page_size,
                'count': total_products,
                'next': f'/product/?page={self.page.number+1}',
                'previous': f'/product/?page={self.page.number-1}',
                'results': serializer.data,
            }
            print("first:",context['next'])
            return Response(context, status=status.HTTP_200_OK)
        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
  
  
class ProductViewset(ProductPagination,ReadOnlyModelViewSet):
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, SearchFilter,OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['title','unit_price', 'last_update']
    renderer_classes=[TemplateHTMLRenderer]
    
    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return ProductCartSerializer
        else:
            return ProductSerializer
    def get_serializer_context(self):
        return {'request':self.request}
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            customer = Customer.objects.get(user=self.request.user)
            return Product.objects.prefetch_related(
                'images',
                Prefetch(
                    'cartitem_set',queryset=CartItem.objects.only('id','quantity').filter(customer=customer),
                         to_attr='cart_items'
                         )
                ).select_related('brand', 'category').filter(active=True)
        return Product.objects.prefetch_related('images').\
            select_related('brand').select_related('category').\
                filter(active=True)
    
    def get_template_names(self) -> list[str]:
        if self.action == 'list':
            return ["app/products-list.html"]
        else:
            return ["app/product_page.html"]
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset,request=request)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            context={
                'product':serializer.data,
            }
            return Response(context)
        except:
            messages.info(request,"That Product is currently unavailable")
            return redirect('product_list')
    

#not completed
class BrandViewSet(ReadOnlyModelViewSet):
    queryset=Brand.objects.annotate(products_count=Count('brand_products')).filter(active=True)
    pagination_class=CustomPagination
    serializer_class=BrandDetailsSerializer
    permission_classes=[AllowAny]
    renderer_classes=[TemplateHTMLRenderer]
    
    def get_template_names(self) -> list[str]:
        if self.action == 'retrieve':
            return ["app/brand.html"]
        return ["app/brandslist.html"]
    
    
    
    def get_serializer_context(self):
        return {'request':self.request}
    

#not completed  
class CategoryViewSet(ReadOnlyModelViewSet):
    queryset=Main_Category.objects.annotate(products_count=Count('categories_products')).filter(active=True)
    pagination_class=CustomPagination
    serializer_class=CategorySerializer
    permission_classes=[AllowAny]
    renderer_classes=[TemplateHTMLRenderer]
    
    def get_template_names(self) -> list[str]:
        if self.action == 'retrieve':
            return ["app/category.html"]
        return ["app/categorylist.html"]
    
    
    
    def get_serializer_context(self):
        return {'request':self.request}
    

class CartViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    renderer_classes=[TemplateHTMLRenderer]
    
    # def get_template_names(self) -> list[str]:
    #     if self.action in ['list']:
    #         return ["app/cart.html"]
        
    def get_customer_id(self):
        return Customer.objects.only('id').get(user_id=self.request.user.id)
    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'customer_id':self.get_customer_id().id
        }
    def get_serializer_class(self):
        if self.action in ['list','retrieve']:
            return CartSerializer
        return CartCUSerializer
    def get_queryset(self):
        customer_id=self.get_customer_id().id
        return CartItem.objects.select_related('product').filter(customer=customer_id)
    def list(self, request, *args, **kwargs):
        mode=None
        if bool(request.GET):
            print(request.GET)
            mode=request.GET['mode']
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response= self.get_paginated_response(serializer.data)
            response.content_type="text/html"
            if mode is None:
                response.template_name="app/cart.html"
                return response
            elif mode =="checkout":
                response.template_name="app/checkout.html"
                return response
                
            

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        print(request.data)
        data={key: value for key, value in request.data.items()}
        mode=data.pop('mode')
        page=data.pop('in')
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            instance,message=serializer.save(mode=mode)
            cartserializer=CartSerializer(instance=instance)
            cart=cartserializer.data
            messages.error(request,message=message)
            if page== 'list':
                context={
                "item":cart
                }
                response=Response(context,template_name="app/cart-add-listpage.html",content_type="text/html")
                return response
            elif page == 'detail':
                context={
                "item":cart
                }
                response=Response(context,template_name="app/cart-add-detailpage.html",content_type="text/html")
                return response
            
        else:
            messages.error(request,"Error in Adding to cart")
            context={
                "item":instance
            }
            return Response(context,template_name="app/cart-list.html",content_type="text/html")
            
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        messages.warning(request,f"{instance.product.title} has been removed from cart")
        self.perform_destroy(instance)
        return Response(template_name="app/nav-update.html",content_type="text/html")
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        context={
            "serializer":serializer,
            "item":serializer.data
        }
        return Response(context,template_name="app/cart-del.html",content_type="text/html")
    
    def update(self, request, *args, **kwargs):
        data={key: value for key, value in request.data.items()}
        print(data)
        mode=data.pop('mode')
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            instance,message=serializer.save(mode=mode)
            cartserializer=CartSerializer(instance=instance)
            cart=cartserializer.data
            print(cart)
            messages.info(request,message=message)
            context={
                "item":cart
            }
            response=Response(context,template_name="app/cart-list.html",content_type="text/html")
            return response
        else:
            messages.error(request,"Error in updating quantity")
            context={
                "item":instance
            }
            return Response(context,template_name="app/cart-list.html",content_type="text/html")

class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'head', 'options']
    renderer_classes=[TemplateHTMLRenderer]
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        customer_id = Customer.objects.only('id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)
    
    def get_customer_id(self):
        return Customer.objects.only('id').get(user_id=self.request.user.id)
    
    def get_serializer_class(self):
        if self.action in ['create','update']:
            return CreateOrderSerializer
        elif self.action in ['update']:
            return UpdateOrderSerializer
        elif self.action in ['list','retieve']:
            return OrderSerializer
    
    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'customer':self.get_customer_id()
        }
    
   
    def list(self, request, *args, **kwargs):
        mode=None
        if bool(request.GET):
            print(request.GET)
            mode=request.GET['mode']
        if mode=="checkout":
            # customer=self.get_customer_id()
            # address=Address.objects.filter(customer=customer.id)
            serializer=CreateOrderSerializer()
            messages.warning(request,"Please select an address to place the order")
            context={
                'serializer':serializer,
            }
            return Response(context,template_name="app/order-add.html",content_type="text/html")
        elif mode=="profile":
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response= self.get_paginated_response(serializer.data)
                response.template_name="app/order-list.html"
                response.content_type="text/html"
                return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data,context={'customer':self.get_customer_id()}
            )
        if serializer.is_valid():
            order,message = serializer.save()
            serializer = OrderSerializer(order)
            messages.success(request,message)
            context={
                'order':serializer.data
            }
            return Response(context,template_name='app/order-summary.html',content_type='text/html')
        else:
            pass
        
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            pass
    
    # def destroy(self, request, *args, **kwargs):
    #     return super().destroy(request, *args, **kwargs) 
    

    
    
    
        
    
    
    
        
    
