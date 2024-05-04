from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator,RegexValidator
from django.db.models.functions import Coalesce
from django.conf import settings
from django.contrib import admin
from uuid import uuid4


class Discount(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()
    active = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    

class Main_Category(models.Model):
    title = models.CharField(max_length=100)
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
    discount = models.ManyToManyField(Discount, blank=True)
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
        
class Wallet(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.username}'s Wallet"

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    pin = models.CharField(max_length=10,
        validators= [ RegexValidator(
                        regex=r'^\d{6}$',
                        message='Pin number should be 6 digit number.')
                        ]
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE)


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='o_customer')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='order')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="orderitems")
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)





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
