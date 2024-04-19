from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.db.models.aggregates import Count
from .models import Product,Collection
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
#from rest_framework.response import SimpleTemplateResponse
from rest_framework.viewsets import ModelViewSet, GenericViewSet
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
        queryset = Product.objects.prefetch_related('images').select_related('collection').select_related('category').filter(active=True)
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
    
    
    
class CollectionListView(APIView, PageNumberPagination):
    """
    API view to get a paginated list of active collections with additional features.
    """
    pagination_class = PageNumberPagination
    renderer_classes = [TemplateHTMLRenderer] 
    template_name = 'app/collectionslist.html'  

    def get(self, request, format=None):
        """
        Get a list of active collections with product count and pagination.
        """
        queryset = Collection.objects.annotate(products_count=Count('collection_products')).filter(active=True)
        page = self.paginate_queryset(queryset, request)
        if page is not None:
            serializer = CollectionDetailsSerializer(page, many=True)
            print(serializer.data)
            total_collections = queryset.count()
            context = {
                'total_pages': self.get_page_count(total_collections, self.page_size),
                'page_number': self.page.number,
                'page_size': self.get_page_size(request),
                'count': total_collections,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': serializer.data,
            }
            return Response(context, status=status.HTTP_200_OK)
        serializer = CollectionDetailsSerializer(queryset, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_page_count(self, total_collections, page_size):
        """Calculates the total number of pages based on collection count and page size."""
        return (total_collections // page_size) + (total_collections % page_size > 0)


        

#---PRoduct view to display or edit or delete specified one product
class ProductDetailView(APIView):
    """
    API view to get details of a specific product.
    """

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
            return Response(serializer.data)
        return Response()


  
  
class CollectionDetails(APIView):
    """
    API view to get a paginated list of active collections with HTML template rendering.
    """
    pagination_class = PageNumberPagination
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'app/collectionslist.html'  # Assuming template location
    page_size=5

    def get(self,request,pk):
        try:
            
            collection=get_object_or_404(
                Collection.objects.annotate(
                    products_count=Count('collection_products')
                ).filter(active=True),id=pk
            )
        except:
            collection=None
        serializer=CollectionDetailsSerializer(collection)
        return Response(serializer.data)

        
        

    
#class ReviewSet(ModelViewSet)
class CartViewSet(ModelViewSet):
    queryset=CartItem.objects.filter()#complete query (get_query)
    serializer_class=CartSerializer
    



class CustomerViewSet(APIView):
    def get(self,request):
        pass
    def post(self,request):
        pass
    def post(self,request):
        pass
        
    
