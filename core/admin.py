from django.contrib import admin
from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem
from django.contrib.contenttypes.admin import GenericTabularInline

# Register your models here.
class TagInline(GenericTabularInline):
    autocomplete_fields=['tag']
    model=TaggedItem


class CutomProductAdmin(ProductAdmin):
    inlines=[TagInline]
    
    
admin.site.unregister(Product)
admin.site.register(Product,CutomProductAdmin)