from django.contrib import admin
from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem
from django.contrib.auth.admin import UserAdmin as baseUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import User

# Register your models here.

@admin.register(User)
class UserAdmin(baseUserAdmin):
    add_fieldsets = (
    (
        None,
        {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2","email","phone","first_name","last_name"),
        },
    ),
    )
    
    
class TagInline(GenericTabularInline):
    autocomplete_fields=['tag']
    model=TaggedItem


class CutomProductAdmin(ProductAdmin):
    inlines=[TagInline]
    
    
admin.site.unregister(Product)
admin.site.register(Product,CutomProductAdmin)