from decimal import Decimal
from store.models import Product, Collection,CartItem,ProductImage,Main_Category
from rest_framework import serializers


class CollectionDetailsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count','img']
    products_count = serializers.IntegerField(read_only=True)
    
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Main_Category
        fields=['id','title','products_count',]
    products_count = serializers.IntegerField(read_only=True)

    

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductImage
        fields=['id','image']       




class ProductSerializer(serializers.ModelSerializer):
    images=ProductImageSerializer(many=True,read_only=True)
    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')
    category=CategorySerializer()
    collection=CollectionDetailsSerializer()
    class Meta:
        model = Product
        fields = ['id', 'title','slug', 'description', 'inventory', 'unit_price', 'price_with_tax', 'collection','images','category']

    

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)
        
        
class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection','images']
        
    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)
    


   
    
    # def create(self, validated_data):
    #     unpack validated data to corresponding Model
    #     add other field calculate or cutoms
    #     call save ()        
    #     return Model name here
    
    # def update(self, instance, validated_data):
    #     update instance with validated data
    #     call save for instance        
    #     return instance here
    

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=['id', 'title', 'description', 'unit_price']


class CartSerializer(serializers.ModelSerializer):
    product=SimpleProductSerializer()
    class Meta:
        model=CartItem
        fields=['id','created_at','quatity','product']
        