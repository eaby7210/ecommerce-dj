from decimal import Decimal
from store.models import Product, Brand,CartItem,ProductImage,Main_Category,Customer
from rest_framework import serializers
from core.serializers import UserSerializer,UserUpdateSerializer


class BrandDetailsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Brand
        fields = ['id', 'title', 'products_count','img','description','active']
    products_count = serializers.IntegerField(read_only=True)
    
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Main_Category
        fields=['id','title','products_count','img','description']
    products_count = serializers.IntegerField(read_only=True)

class CategoryAdminSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)
    active=serializers.BooleanField(default=False)
    class Meta:
        model=Main_Category
        fields=['id','title','products_count','img','description','active']
    

class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id=self.context['product_id']
        return ProductImage.objects.create(product_id=product_id,**validated_data)
    class Meta:
        model=ProductImage
        fields=['id','image']       




class ProductSerializer(serializers.ModelSerializer):
    images=ProductImageSerializer(many=True,read_only=True)
    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')
    stock=serializers.SerializerMethodField(method_name='stock_status')
    category=CategorySerializer()
    brand=BrandDetailsSerializer()
    class Meta:
        model = Product
        fields = ['id', 'title','slug', 'description', 'inventory', 'unit_price','rating', 'price_with_tax', 'brand','images','category','active','stock']

    def stock_status(self,product:Product):
        if product.inventory==0:
            return "Out of Stock"
        elif product.inventory<=10:
            return "Only few left"
        else:
            return None

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)
    
    
class ProductAdminSerializer(serializers.ModelSerializer):
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    class Meta:
        model = Product
        fields = ['id', 'title','slug', 'description', 'inventory', 'unit_price', 'price_with_tax','rating', 'brand','category','active']

    

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)
        
        
class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection','images','active']
        
    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)

class SimpleProductSerializer(serializers.ModelSerializer):
    stock=serializers.SerializerMethodField(method_name='stock_status')
    
    def stock_status(self,product:Product):
        if product.inventory==0:
            return "Out of Stock"
        elif product.inventory<=10:
            return "Only few left"
        else:
            return None
    class Meta:
        model=Product
        fields=['id', 'title', 'unit_price','stock']


class CartSerializer(serializers.ModelSerializer):
    product=SimpleProductSerializer(read_only=True)
    total_price=serializers.SerializerMethodField()
    
    def get_total_price(self,cart_item:CartItem):
        return cart_item.product.unit_price*cart_item.quantity
    class Meta:
        model=CartItem
        fields=['id','quantity','product','customer','total_price']
        
class CartCUSerializer(serializers.ModelSerializer):
    product_id=serializers.IntegerField()
    customer_id=serializers.IntegerField(read_only=True)
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'No product with the given ID was found.')
        return value
    def save(self,**kwargs):
        product_id = self.validated_data['product_id']
        customer_id=self.context['customer_id']
        quantity=self.validated_data['quantity']
        mode = kwargs.pop('mode', None)
        
        try:
            cart_item=CartItem.objects.get(
                product_id=product_id,
                customer_id=customer_id,
            )
            if mode=="add":
                cart_item.quantity+=quantity
            elif mode=="update":
                cart_item.quantity=quantity
            elif mode=="minus":
                cart_item.quantity-=quantity
            cart_item.save()
            self.instance=cart_item
        except CartItem.DoesNotExist:
            self.instance=CartItem.objects.create(
                customer_id=customer_id,
                **self.validated_data
            )
        return self.instance
        
    class Meta:
        model=CartItem
        fields=['id','quantity','product_id','customer_id']
        
        
class CustomerSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    class Meta:
        model=Customer
        fields=['id','membership','birth_date','user']
        
class CustomerUpdateSerializer(serializers.ModelSerializer):
    user=UserUpdateSerializer()
    class Meta:
        model=Customer
        fields=['id','membership','birth_date','user']
        
        
class CustomerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields=['id','membership','birth_date','user']
        