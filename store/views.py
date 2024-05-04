from django.http import HttpResponse,JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models.aggregates import Count
from .models import Product,Brand,Address
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .filters import *
#from rest_framework.response import SimpleTemplateResponse
from rest_framework.viewsets import ModelViewSet, GenericViewSet,ReadOnlyModelViewSet
from rest_framework.renderers import TemplateHTMLRenderer
#from rest_framework.mixins.
from rest_framework import status
import pprint

# Create your views here.

class ProductListView(APIView, PageNumberPagination):
    """
    API view to get a paginated list of active products with HTML template rendering.
    """
    pagination_class = PageNumberPagination
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'app/products.html'  # Assuming template location
    page_size=20

    def get(self, request, format=None):
        """
        Get a list of active products.
        """
        queryset = Product.objects.prefetch_related('images').select_related('brand').select_related('category').filter(active=True)
        page = self.paginate_queryset(queryset,request)
        if page is not None:
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
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': serializer.data,
            }
            return Response(context, status=status.HTTP_200_OK)
        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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
    
      
#---PRoduct view to display or edit or delete specified one product
class ProductDetailView(APIView):
    """
    API view to get details of a specific product.
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'app/product_page.html'
    
    

    def get(self, request, pk, format=None):
        """
        Retrieve details of a product with the given primary key (pk).
        """
        try:
            product = Product.objects.prefetch_related('images').get(pk=pk, active=True)
        except Product.DoesNotExist:
            product=None
        if bool(product):
            serializer = ProductSerializer(product)
            context={
                'serializer':serializer,
                'product':serializer.data
            }
            print(serializer.data)
            return Response(context)
        messages.info(request,"That Product is currently unavailable")
        return redirect('product_list')
  
    
#class ReviewSet(ModelViewSet)
class CartViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    renderer_classes=[TemplateHTMLRenderer]
    
    def get_template_names(self) -> list[str]:
        if self.action in ['list']:
            return ["app/cart.html"]
        
    
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
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    def update(self, request, *args, **kwargs):
        data={key: value for key, value in request.data.items()}
        print(data)
        mode=data.pop('mode')
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        if serializer.is_valid():
            instance=serializer.save(mode=mode)
            cartserializer=CartSerializer(instance=instance)
            cart=cartserializer.data
            print(cart)
            return HttpResponse(
                f'<span class="col">Quantity: {cart['quantity']}</span> <span class="text-center col">Total Price: ${cart['total_price']}</span>'
                )

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


    
class AddressView(APIView):
    renderer_classes=[TemplateHTMLRenderer]
    
    def get_queryset(self):
        
        return Address.objects.filter(customer=self.request.user.customer)
    
    def get_template_names(self) -> list[str]:
        if self.request.method in ['GET']:
            return [""]
    def get(self,request):
        pass
    
    def post(self,request):
        pass
    
    def put(self,request):
        pass
    
    def delete(self,request):
        pass
    
        
    
    
    
        
    
