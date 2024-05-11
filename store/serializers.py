from decimal import Decimal
from store.models import Product,Brand,CartItem,ProductImage,Main_Category,Customer,Order,OrderItem
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

class CartSimpleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CartItem
        fields=['id','quantity','customer']

class ProductCartSerializer(serializers.ModelSerializer):
    images=ProductImageSerializer(many=True,read_only=True)
    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')
    stock=serializers.SerializerMethodField(method_name='stock_status')
    category=CategorySerializer()
    brand=BrandDetailsSerializer()
    cart_items=CartSimpleSerializer(many=True)
    class Meta:
        model = Product
        fields = ['id', 'title','slug', 'description', 'inventory', 'unit_price','rating', 'price_with_tax', 'brand','images','category','active','stock','cart_items']

    def stock_status(self,product:Product):
        if product.inventory==0:
            return "Out of Stock"
        elif product.inventory<=10:
            return "Only few left"
        else:
            return None

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)
      
class ProductSerializer(serializers.ModelSerializer):
    images=ProductImageSerializer(many=True,read_only=True)
    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')
    stock=serializers.SerializerMethodField(method_name='stock_status')
    category=CategorySerializer()
    brand=BrandDetailsSerializer()
    class Meta:
        model = Product
        fields = ['id', 'title','slug', 'description', 'inventory', 'unit_price','rating', 'price_with_tax', 'brand','images','category','active','stock',]

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
        product=Product.objects.only('inventory','title').get(pk=product_id)
        try:
            cart_item=CartItem.objects.get(
                product_id=product_id,
                customer_id=customer_id,
            )
            if mode=="add":
                if cart_item.quantity+quantity >10:
                    message=f"Cannot order more 10 per order"
                    cart_item.quantity=10
                elif cart_item.quantity+quantity > product.inventory:
                    if product.inventory ==0:
                        message="Item is currently Out of stock. Please try again later"
                    else:
                        message=f"Cannot order more than that of in the stock"
                    cart_item.quantity=product.inventory
                else:    
                    cart_item.quantity+=quantity
                    message=f'Quantity of item {product.title} changed to "{cart_item.quantity}"'
            elif mode=="update":
                if quantity >10:
                    message=f"Cannot order more 10 per order"
                    cart_item.quantity=10
                elif quantity > product.inventory:
                    if product.inventory ==0:
                        message="Item is currently Out of stock. Please try again later"
                    else:
                        message=f"Cannot order more than that of in the stock"
                    cart_item.quantity=product.inventory
                elif quantity <1:
                    message="Quantity cannot be less than 1"
                    cart_item.quantity=1
                else:
                    cart_item.quantity=quantity
                    message=f'Quantity of item {product.title} changed to "{cart_item.quantity}"'
            elif mode=="minus":
                if cart_item.quantity-quantity<1:
                    message="Quantity cannot be less than 1"
                    cart_item.quantity=1
                else:
                    cart_item.quantity-=quantity
                    message=f'Quantity of item {product.title} changed to "{cart_item.quantity}"'
            cart_item.save()
            self.instance=cart_item
        except CartItem.DoesNotExist:
            if mode=="add":
                if quantity<1:
                    message="Quantity cannot be less than 1"
                    return None,message
                elif quantity> product.inventory:
                    message=f"Quantity cannot be more than that of in the stock (Added {product.inventory}items to cart)"
                    quantity=product.inventory
                else:
                    message=f'{product.title} successfully added to the cart'
            self.instance=CartItem.objects.create(
                customer_id=customer_id,
                product_id = product.id,
                quantity=quantity,
                )
            
        return self.instance,message
        
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
 

class OrderItemSerializer(serializers.ModelSerializer):
    product=SimpleProductSerializer()
    class Meta:
        model=OrderItem 
        fields=['id','product','unit_price','quantity']
        
        
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']