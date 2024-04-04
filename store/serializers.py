from decimal import Decimal
from store.models import Product, Collection
from rest_framework import serializers


class CollectionDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection']

    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

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
    
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model=ReviewSerializerfields=[
            'id','date',
            'name','description',
            'product','rating'
        ]