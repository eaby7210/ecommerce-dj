from decimal import Decimal
from django.db import transaction
from django.urls import reverse
from django.conf import settings
from .models import *
from rest_framework import serializers
from core.serializers import UserSerializer,UserUpdateSerializer,UserNormalUpdateSerializer
import razorpay



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
    

class CartSimpleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CartItem
        fields=['id','quantity','customer']


      
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
    rating=serializers.CharField(read_only=True)
    effective_price=serializers.SerializerMethodField(method_name="get_effective_price")
    class Meta:
        model = Product
        fields = ['id', 'title','slug', 'description', 'inventory', 'unit_price','rating', 'price_with_tax', 'brand','images','category','active','stock','offer_percent','offer_start','offer_end','effective_price']

    def get_effective_price(self,product:Product):
        
        return product.effective_price()
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
    effective_price=serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'title','slug', 'description', 'inventory', 'unit_price', 'price_with_tax', 'brand','category','active','offer_percent','offer_start','offer_end','effective_price']

    def get_effective_price(self,product:Product):
        return product.effective_price()
    

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
    image=serializers.SerializerMethodField()
    effective_price=serializers.SerializerMethodField(method_name="get_effective_price")
    def get_image(self,product:Product):
        first_img=product.images.first()
        return str(first_img.image) if bool(first_img) else None
    
    def get_effective_price(self,product:Product):
        return product.effective_price()
    
    def stock_status(self,product:Product):
        if product.inventory==0:
            return "Out of Stock"
        elif product.inventory<=10:
            return "Only few left"
        else:
            return None
    class Meta:
        model=Product
        fields=['id', 'title', 'unit_price','stock','image','effective_price']


class CartSerializer(serializers.ModelSerializer):
    product=SimpleProductSerializer(read_only=True)
    total_price=serializers.SerializerMethodField()
    
    def get_total_price(self,cart_item:CartItem):
        return cart_item.product.effective_price()*cart_item.quantity
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
                elif product.inventory<1:
                    message="Item is currently Out of stock. Please try again later"
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
        fields=['id','membership','birth_date','wallet_balance','user']



class CustomerProfiledSerializer(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields=['id','birth_date','wallet_balance']
        
class CustomerUpdateSerializer(serializers.ModelSerializer):
    user=UserUpdateSerializer()
    class Meta:
        model=Customer
        fields=['id','membership','birth_date','user']
              
class CustomerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields=['id','membership','birth_date','user']
        
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model=Address
        fields=['id','name','state','city','pin']
 
def razor_payment(order):
        razorpay_client=razorpay.Client(auth=(settings.RAZORPAY_ID, settings.RAZORPAY_ACCOUNT_ID))
                
        razorpay_order = razorpay_client.order.create(
            dict(
                amount=int(order.grand_total*100),
                currency='INR',
                receipt=str(order.id),
                payment_capture='0'
                )
            )
        razorpay_order_obj=RazorpayOrders.objects.create(order=order,id=razorpay_order['id'])
        order.payment_status='F'
        order.order_status='FL' 
        order.save()
        return razorpay_order_obj,int(order.grand_total*100)
        
class OrderItemSerializer(serializers.ModelSerializer):
    product=SimpleProductSerializer()
    str_status=serializers.SerializerMethodField()
    
    def get_str_status(self,item:OrderItem):
        return item.get_status_display()
    
    class Meta:
        model=OrderItem 
        fields=['id','product','quantity','status','str_status','unit_price']
        
        
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    address=AddressSerializer()
    payment_status=serializers.SerializerMethodField()
    order_status=serializers.SerializerMethodField()
    name=serializers.SerializerMethodField()
    customer=CustomerSerializer()

    class Meta:
        model = Order
        fields = [
            'id','name', 'customer', 'placed_at','address', 'payment_status','payment_method',
            'order_status','total', 'items','applied_coupon','grand_total',
            ]
    
    def get_payment_status(self,order:Order):
        return order.get_payment_status_display()
    def get_order_status(self,order:Order):
        return order.get_order_status_display()
    def get_name(self,order:Order):
        return str(order)
        
class CreateOrderSerializer(serializers.Serializer):
    address=serializers.CharField()
    
        
    def validate_address(self,address):
        try:
            address_obj=Address.objects.get(id=address)
        except:
            raise serializers.ValidationError('Address does not exist')
        return address_obj
    
    def validate(self, attrs):
        customer = self.context['customer']
        if not CartItem.objects.filter(customer=customer).exists():
            raise serializers.ValidationError('Your Cart is empty')
        return attrs
    

    def save(self, **kwargs):
        coupon = kwargs.get('coupon')
        payment_method = kwargs.get('payment_method')
        customer = self.context['customer']
        
        cart_items = CartItem.objects.select_related('product').filter(customer=customer)
        if not cart_items.exists():
            message="Your cart is empty."
            return message, None, None

        total = Decimal(0)
        order_items = []
        total_discount = Decimal(0)

        # Check if all items can be added to the order
        for item in cart_items:
            if item.product.inventory <= 0:
                message = f"Product {item.product.title} is out of stock."
                return message, None, None
            if item.product.inventory < item.quantity:
                message = f"Insufficient quantity for product {item.product.title}."
                return message, None, None

            order_items.append(OrderItem(
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.effective_price()
            ))
            total += item.product.effective_price() * item.quantity

        # Check if the payment method is COD and total is above Rs 1000
        if payment_method == 'cod' and total > 1000:
            message = "Orders above ₹1000 are not allowed for Cash on Delivery (COD)"
            return message, None, None

        if coupon:
            try:
                coupon_obj = Coupon.objects.get(code=coupon)
                discount_amt = total * (coupon_obj.discount / Decimal(100))
                total_discount += discount_amt
                grand_total = total - discount_amt
            except Coupon.DoesNotExist:
                message = "Entered Invalid coupon code"
                return message, None, None
        else:
            grand_total = total

        # Check if the grand total is 0
        if grand_total == 0:
            payment_status = 'C'  # Complete
        else:
            payment_status = 'P'  # Pending

        # Proceed with creating the order and order items
        with transaction.atomic():
            address = self.validated_data['address']
            order_address = OrderAddress.objects.create(
                name=address.name,
                state=address.state,
                city=address.city,
                pin=address.pin,
                other_details=address.other_details
            )
            new_order = Order.objects.create(
                customer=customer,
                address=order_address,
                total=total,
                total_discount=total_discount,
                payment_method=payment_method,
                payment_status=payment_status,
                order_status='PL'
            )

            for order_item in order_items:
                order_item.order = new_order
                product = Product.objects.get(id=order_item.product.id)
                product.inventory -= order_item.quantity
                product.save()

            OrderItem.objects.bulk_create(order_items)

            new_order.grand_total = grand_total
            if coupon:
                new_order.applied_coupon = coupon_obj
            new_order.save()

            # Delete cart items only after order creation
            cart_items.delete()

            if grand_total == 0:
                message = "Your order is placed successfully with a grand total of ₹0"
                return message, new_order, None
            elif payment_method == 'rzr':
                razorpay_order_obj, total = razor_payment(new_order)
                message = "Please complete the payment through Razorpay Gateway"
                return message, razorpay_order_obj, total
            elif payment_method == 'cod':
                message = "Your order is placed successfully"
                return message, new_order, total



class UpdateAdminOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status','order_status']
        
class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model=Coupon
        fields=['id','code']
        
class CouponCUSerializer(serializers.ModelSerializer):
    class Meta:
        model=Coupon
        fields=['id','name','code','valid_from','valid_to','discount','active']
        
        def validate(self, data):
            """
            Check that valid_from is earlier than valid_to.
            """
            valid_from = data.get('valid_from')
            valid_to = data.get('valid_to')
            print(valid_from," --- ",valid_to)
            
            if valid_from and valid_to:
                if valid_to <= valid_from:
                    raise serializers.ValidationError("Valid To date must be after Valid From date.")
            else:
                raise serializers.ValidationError("valid from and to Must mout be empty")

            return data
        
class RazorSerializer(serializers.ModelSerializer):
    order=OrderSerializer()
    class Meta:
        model=RazorpayOrders
        fields=['id','order']
        
class WishListSerializer(serializers.ModelSerializer):
    product=SimpleProductSerializer(read_only=True)
    class Meta:
        model=WishList
        fields=['id','product','customer']
        
class CheckWishListSerializer(serializers.ModelSerializer):
    class Meta:
        model=WishList
        fields=['id','customer']
        
class CreateWhishSerializer(serializers.Serializer):
    product_id=serializers.IntegerField()
    
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'No product with the given ID was found.')
        return value
    
    def save(self,*args, **kwargs):
        
        product_id=self.validated_data['product_id']
        customer=self.context['customer']
        product=Product.objects.only('title').get(pk=product_id)
        try:
            self.instance=WishList.objects.get(product_id=product_id,customer=customer)
            
            self.instance.delete()
            status=False
            message=f"{product.title} removed from whishlist"
        except WishList.DoesNotExist as e:
            self.instance=WishList.objects.create(
                customer=customer,
                product_id = product_id,
            )
            status=True
            message=f"{product.title} added to whishlist"
        return self.instance,message,status
    
    
class ProductCartSerializer(serializers.ModelSerializer):
    images=ProductImageSerializer(many=True,read_only=True)
    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')
    stock=serializers.SerializerMethodField(method_name='stock_status')
    category=CategorySerializer()
    brand=BrandDetailsSerializer()
    cart_items=CartSimpleSerializer(many=True)
    wishlist_items=CheckWishListSerializer(many=True,read_only=True)
    effective_price=serializers.SerializerMethodField(method_name="get_effective_price")
    class Meta:
        model = Product
        fields = ['id', 'title','slug', 'description', 'inventory', 'unit_price','rating', 'price_with_tax', 'brand','images','category','active','stock','cart_items','wishlist_items','offer_percent','offer_start','offer_end','effective_price']

    def get_effective_price(self,product:Product):
        return product.effective_price()
    
    def stock_status(self,product:Product):
        if product.inventory==0:
            return "Out of Stock"
        elif product.inventory<=10:
            return "Only few left"
        else:
            return None

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)
    
    
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'customer', 'order', 'amount', 'transaction_type', 'created_at']
