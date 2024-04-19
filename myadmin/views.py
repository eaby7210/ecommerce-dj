from django.shortcuts import render,get_object_or_404
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.db.models.aggregates import Count
from store.models import *
from store.serializers import *
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

# Create your views here.


class ProductViewSet(ModelViewSet):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer
    filter_backends=[DjangoFilterBackend]
    filterset_fields=['collection_id']
    pagination_class=PageNumberPagination
    permission_classes=[IsAdminUser]
    
    # def get_queryset(self):
        #customise query set along with self.request.query_params(dict) here (use get())
        #make queryset=newqueryset
    
    def get_serializer_context(self):
        return {'request':self.request}
    
    def destroy(self,request,*args, **kwargs):
        # product=get_object_or_404(Product,pk=pk)
        # if product.orderitems.count()>0:
        if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
            return Response({'error':'Product cannot be deleted Since there are orders assossiated with this product'})
        return super().destroy(request,*args, **kwargs)
    
    

class CollectionViewSet(ModelViewSet):
    queryset=Collection.objects.annotate(
        products_count=Count('collection_products')).all()
    permission_classes=[IsAdminUser]
    serializer_class=CollectionDetailsSerializer
    
    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']):
            return Response({'error':'Collection cannot be deleted since assosiated Products still exists.'})
        return super().destroy(request, *args, **kwargs)

    
    

# class CollectionList(ModelViewSet):
#     pass

# class CollectionDetails(ModelViewSet):
#     pass