from django.db.models.aggregates import Count
from typing import Any
from django.contrib import admin,messages

from django.urls import reverse
from django.db.models.query import QuerySet
from django.utils.html import format_html,urlencode
from django.http import HttpRequest

from . import models
# Register your models here.

class InventoryFilter(admin.SimpleListFilter):
    title='Inventory'
    parameter_name='inventory'
    
    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [
            ('0','Out of Stock'),
            ('<10','Low'),
        ]
    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() =='0':
            return queryset.filter(inventory=0)
        elif self.value() == '<10':
            return queryset.filter(inventory__lt=10)

class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ['thumbnail']

    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html(f'<img src="{instance.image.url}" class="thumbnail" />')
        return ''


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields={
        'slug':['title']
    }
    search_fields=['title']
    actions=['clear_inventory']
    inlines = [ProductImageInline]
    autocomplete_fields=['brand']
    list_display=['title','unit_price','inventory_status','brand_title']
    list_editable=['unit_price']
    list_filter=['category','brand','last_update',InventoryFilter]
    list_per_page=10
    list_select_related=['brand']
    
    def brand_title(self,product):
        return product.brand.title
    
    @admin.display(ordering='inventory')
    def inventory_status(self,product):
        if product.inventory==0:
            return "Out of Stock"
        elif product.inventory<10:
            return "Low"
        return "OK"
    
    @admin.action(description='Clear inventory')
    def clear_inventory(self,request,queryset):
        updated_count=queryset.update(inventory=0)
        self.message_user(request,f'{updated_count} Products were successfully updated',messages.INFO)
        
    class Media:
        css = {
            'all': ['store/styles.css']
        }
        
class WhishListInline(admin.TabularInline):
    model=models.WishList           
    
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_editable=['membership'] 
    list_display=['first_name','last_name','membership']
    list_per_page=10
    inlines=[WhishListInline]
    list_select_related=['user']
    ordering=['user__first_name','user__last_name']
    search_fields=['first_name__istartswith','last_name__istartswith']
    
@admin.register(models.Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display=['name','code','valid_from','valid_to','discount','active']
    list_filter=['valid_from','valid_to','discount','active']
    

@admin.register(models.Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display=['title','products_count']
    search_fields=['title']
    
    @admin.display(ordering='products_count')
    def products_count(self,brand):
        url=(
            reverse('admin:store_product_changelist')+
            '?'+
            urlencode({
                'brand__id':str(brand.id)
                })
            )
        return format_html('<a href="{}">{}</a>',url,brand.products_count)
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count=Count('brand_products'))
    
@admin.register(models.Main_Category)
class Main_CategoryAdmin(admin.ModelAdmin):
    list_display=['title','products_count']
    search_fields=['title']
    
    @admin.display(ordering='products_count')
    def products_count(self,brand):
        url=(
            reverse('admin:store_product_changelist')+
            '?'+
            urlencode({
                'brand__id':str(brand.id)
                })
            )
        return format_html('<a href="{}">{}</a>',url,brand.products_count)
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count=Count('categories_products'))

class OrderItemInline(admin.TabularInline):
    extra=1
    min=1
    max=10
    autocomplete_fields=['product']
    model=models.OrderItem

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields=['customer']
    list_display=['id','placed_at','payment_status','customer','user_membership']
    inlines=[OrderItemInline]
    ordering=['-payment_status','placed_at']
    list_select_related=['customer']
    
    @admin.display(ordering='customer__membership')
    def user_membership(self,order):
        return order.customer.membership
    
@admin.register(models.Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'display_order', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    ordering = ('display_order', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    
        


