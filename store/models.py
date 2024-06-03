from django.db import models,transaction
from django.core.validators import MinValueValidator, MaxValueValidator,RegexValidator
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from django.conf import settings
from django.contrib import admin
# from django.db.models.functions import Coalesce
# from uuid import uuid4


    
def validate_valid_from(value):
    """
    Validator to ensure valid_from is greater than today's date.
    """
    if value <= date.today():
        raise ValidationError('Valid From date must be today or in the future.')

def validate_valid_to(value):
    """
    Validator to ensure valid_to is one day greater than valid_from.
    """
    if value <= value.valid_from:  
        raise ValidationError('Valid To date must be same as or one day after Valid From date.')

    
class Coupon(models.Model):
    code=models.CharField(max_length=50,unique=True,validators=[RegexValidator(
        regex=r'^[A-Z0-9]{1,10}$',
        message='Please use uppercase letters and numbers only (up to 10 characters).'
    )])
    name=models.CharField(max_length=50)
    valid_from=models.DateField( validators=[validate_valid_from])
    valid_to=models.DateField(validators=[validate_valid_to])
    discount=models.DecimalField(max_digits=5, decimal_places=2,validators=[
        MinValueValidator(0),MaxValueValidator(100)
        ]
        )
    active=models.BooleanField(default=False)
    
    def _str__(self):
        return self.name
    
    class Meta:
        unique_together = (('name', 'discount'),)
        ordering=['-valid_to']
    

class Main_Category(models.Model):
    title = models.CharField(max_length=100,unique=True)
    description = models.TextField(default='Default Description')
    img = models.ImageField(upload_to='store/categories', default='null', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=False)


    def __str__(self):
        return str(self.title)
    class Meta:
        ordering = ['title']


class Brand(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True,blank=True, related_name='f_product')
    img = models.ImageField(upload_to='store/collections', default='null', null=True, blank=True)
    description = models.TextField(default='Default Description',null=True, blank=True)
    active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(1)])
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    last_update = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='brand_products')
    category=models.ForeignKey(Main_Category,null=True,blank=True, on_delete=models.PROTECT, related_name='categories_products')
    rating = models.DecimalField(max_digits=2, decimal_places=1, validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class ProductImage(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images')
    image=models.ImageField(upload_to='store/images')
    
    
class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_GOLD, 'Gold'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_BRONZE, 'Bronze'),
    ]

    birth_date = models.DateField(null=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user')

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        


class Address(models.Model):
    name=models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    pin = models.CharField(max_length=10,
        validators= [ RegexValidator(
                        regex=r'^\d{6}$',
                        message='Pin number should be 6 digit number.')
                        ]
    )
    primary=models.BooleanField(default=False)
    other_details=models.TextField(blank=True,null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name+", "+self.city+', '+self.state
    class Meta:
        ordering=['-primary']
    
class OrderAddress(models.Model):
    name=models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    pin = models.CharField(max_length=10,
        validators= [ RegexValidator(
                        regex=r'^\d{6}$',
                        message='Pin number should be 6 digit number.')
                        ]
    )
    other_details=models.TextField(blank=True,null=True) 

class Order(models.Model):
    # Payment status
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]
    
    # Order status
    ORDER_STATUS_FAILED = 'FL'
    ORDER_STATUS_PLACED = 'PL'
    ORDER_STATUS_RETURNED = 'RE'
    ORDER_STATUS_DELIVERED = 'DL'
    ORDER_STATUS_CANCELLED = 'CA'
    ORDER_STATUS_PROCESSING = 'PR'
    ORDER_STATUS_RETURN_REQUESTED = 'RR'
    ORDER_STATUS_COMPLETED = 'CO'
    ORDER_STATUS_CHOICES = [
        (ORDER_STATUS_PLACED, 'Placed'),
        (ORDER_STATUS_PROCESSING, 'Processing'),
        (ORDER_STATUS_CANCELLED, 'Cancelled'),
        (ORDER_STATUS_FAILED, 'Failed'),
        (ORDER_STATUS_DELIVERED, 'Delivered'),
        (ORDER_STATUS_RETURNED, 'Returned'),
        (ORDER_STATUS_COMPLETED, 'Completed'),
        (ORDER_STATUS_RETURN_REQUESTED, 'Return Requested'),
    ]
    
    CASH_ON_DELIVERY = 'cod'
    RAZORPAY = 'rzr'
    PAYMENT_METHOD_CHOICES = [
        (CASH_ON_DELIVERY, 'Cash on Delivery'),
        (RAZORPAY, 'Razorpay')
    ]
    
    address = models.OneToOneField(OrderAddress, on_delete=models.CASCADE, related_name='order_address')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    placed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(max_length=3, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=1, choices=PAYMENT_STATUS_CHOICES)
    order_status = models.CharField(
        max_length=2,
        choices=ORDER_STATUS_CHOICES,
        default=ORDER_STATUS_PLACED
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='o_customer'
    )
    applied_coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, related_name='order_coupons', null=True, blank=True)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payed_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.customer.user.username} {self.id}"
    
    def update_order_status(self):
        items = self.items.all()
        item_statuses = set(item.status for item in items)
        
        if all(status == OrderItem.STATUS_CANCELLED for status in item_statuses):
            self.order_status = self.ORDER_STATUS_CANCELLED
        elif all(status == OrderItem.STATUS_DELIVERED for status in item_statuses):
            self.order_status = self.ORDER_STATUS_DELIVERED
        elif all(status == OrderItem.STATUS_RETURNED for status in item_statuses):
            self.order_status = self.ORDER_STATUS_RETURNED
        elif all(status in {OrderItem.STATUS_DELIVERED, OrderItem.STATUS_RETURNED, OrderItem.STATUS_CANCELLED} for status in item_statuses):
            self.order_status = self.ORDER_STATUS_COMPLETED
        elif OrderItem.STATUS_RETURN_REQUESTED in item_statuses:
            self.order_status = self.ORDER_STATUS_RETURN_REQUESTED
        else:
            self.order_status = self.ORDER_STATUS_PROCESSING
        self.save()
    
    def update_order_items_status(self):
        new_status = None
        if self.order_status == self.ORDER_STATUS_CANCELLED:
            new_status = OrderItem.STATUS_CANCELLED
        elif self.order_status == self.ORDER_STATUS_RETURNED:
            new_status = OrderItem.STATUS_RETURNED
        elif self.order_status == self.ORDER_STATUS_DELIVERED:
            new_status = OrderItem.STATUS_DELIVERED
        
        if new_status:
            self.items.update(status=new_status)
    
    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            self.update_order_items_status()
    
    class Meta:
        ordering = ['-updated_at', '-order_status', '-placed_at']
        indexes = [
            models.Index(fields=['order_status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['customer']),
        ]


class OrderItem(models.Model):
    STATUS_PENDING = 'P'
    STATUS_CANCELLED = 'C'
    STATUS_RETURN_REQUESTED = 'RR'
    STATUS_RETURN_APPROVED = 'RA'
    STATUS_SHIPPED = 'S'
    STATUS_DELIVERED = 'D'
    STATUS_RETURNED = 'RE'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_RETURN_REQUESTED, 'Return Requested'),
        (STATUS_RETURN_APPROVED, 'Return Approved'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_RETURNED, 'Returned'),
    ]
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=STATUS_PENDING)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="orderitems")
    quantity = models.PositiveSmallIntegerField()
    
    def __str__(self) -> str:
        return f"{self.product.title} Q:{self.quantity}"
    
    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            self.order.update_order_status()

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cart_customer')

    class Meta:
        unique_together = [['product', 'customer']]


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='r_product')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='r_customer')
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, validators=[MinValueValidator(1), MaxValueValidator(5)])

class RazorpayOrders(models.Model):
    id=models.CharField(max_length=500,primary_key=True,unique=True)
    order=models.OneToOneField(Order,on_delete=models.CASCADE,related_name='razor_orders')
    rzr_payment_id=models.CharField(max_length=500,null=True,blank=True)
    rzr_signature=models.CharField(max_length=500,null=True,blank=True)
    
    def __str__(self) -> str:
        return str(self.order.id)+" "+str(self.id)
    
class WishList(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="wish_product")
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE,related_name="customer_wish")
    class Meta:
        unique_together=[['product','customer']]
        
        

class ProductDiscount(models.Model):
    name=models.CharField(max_length=50)
    description = models.TextField()
    discount = models.IntegerField(validators=[
        MinValueValidator(0),MaxValueValidator(100)
        ]
        )
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together=[['product','discount']]
    
class BrandDiscount(models.Model):
    name=models.CharField(max_length=50)
    description = models.TextField()
    discount = models.IntegerField(validators=[
        MinValueValidator(0),MaxValueValidator(100)
        ]
        )
    brand=models.ForeignKey(Brand,models.CASCADE)
    active = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together=[['brand','discount']]

class CategoryDiscount(models.Model):
    name=models.CharField(max_length=50)
    description = models.TextField()
    discount = models.IntegerField(validators=[
        MinValueValidator(0),MaxValueValidator(100)
        ]
        )
    category=models.ForeignKey(Main_Category,models.CASCADE)
    active = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together=[['category','discount']]