from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.db.models.aggregates import Count
from .models import Product,Collection
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
#from rest_framework.mixins.
from rest_framework import status

# Create your views here.


#---product views for create a new product or list all products 
@api_view(['GET','POST'])
def product_list(request):
    if request.method=='GET':
        queryset=Product.objects.all()[:10]
        serializer=ProductSerializer(
            queryset,
            many=True,
            context={'request':request}
            )
        return Response(serializer.data)
    elif request.method=='POST':
        serializer=ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("ok",status=status.HTTP_201_CREATED)
           
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        

#---PRoduct view to display or edit or delete specified one product
@api_view(['GET','PUT','DELETE'])
def product_detail(request,pk):
    product=get_object_or_404(Product,pk=pk)
    if request.method=='GET':
        serializer=ProductSerializer(product)
        return Response(serializer.data)
    elif request.method=='PUT':
        serializer=ProductSerializer(product,data=request.data)
        serializer.is_valid(raise_exception=True)#short form for raising 400 error
        serializer.save()
        print(serializer.validated_data)
        return Response("ok")
    elif request.method=='DELETE':
        if product.orderitems_set.count()>0:
            return Response({"error":"Product cannot be Deleted. There are orders still associated with this products"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    
  
  
class CollectionPage(APIView):

    def get(self,request,pk):
        collection=get_object_or_404(
            Collection.objects.annotate(
                products_count=Count('products')
            ),id=pk
        )
        serializer=CollectionDetailsSerializer(collection)
        return Response(serializer.data)
    def put(self,request,pk):
        collection=get_object_or_404(
            Collection.objects.annotate(
                products_count=Count('products')
            ),id=pk
        )
        serializer=CollectionDetailsSerializer(collection,data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        serializer.save()
        return Response("ok")
    def delete(self,request,pk):
        collection=get_object_or_404(
            Collection.objects.annotate(
                products_count=Count('products')
            ),id=pk
        )
        serializer=CollectionDetailsSerializer(collection)
        print(serializer.data)
        if serializer.data["products_count"]>0:
            return Response({"error":"Collection cannot be Deleted. There are products still associated with this collection"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            collection.delete()
            return Response("ok")
            
    
    

# @api_view(['GET','PUT','DELETE'])
# def collection_page(request,pk):
#     collection=get_object_or_404(
#         Collection.objects.annotate(
#             products_count=Count('products')
#             ),id=pk
#         )
#     if request.method=='GET':
#         serializer=CollectionDetailsSerializer(collection)
#         return Response(serializer.data)
#     elif request.method=='PUT':
#         serializer=CollectionDetailsSerializer(collection,data=request.data)
#         serializer.is_valid(raise_exception=True)
#         print(serializer.validated_data)
#         serializer.save()
#         return Response("ok")
        
        
@api_view(['GET','POST'])
def collection_list(request): 
    if request.method=='GET':
        queryset=Collection.objects.annotate(products_count=Count('products')).all()
        serializer=CollectionDetailsSerializer(queryset,many=True)
        return Response(serializer.data)
    elif request.method=='POST':
        serializer=CollectionDetailsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(serializer.validated_data)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
    
#class ReviewSet(ModelViewSet)
        
    
