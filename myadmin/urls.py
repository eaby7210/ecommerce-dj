from django.urls import path
from django.urls.conf import include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

router=routers.SimpleRouter()
router.register('products',views.ProductViewSet,basename='admin-product')
router.register('brand',views.BrandViewSet,basename='admin-brand')
router.register('category',views.CategoryAdminViewSet)
router.register('user',views.UserViewSet,basename="admin-users")

product_router=routers.NestedSimpleRouter(router,'products',lookup='product')
product_router.register('images',views.ProductImageViewSet,basename='product_images')
# print(router.urls)


urlpatterns=[
    path('',views.Dashboard.as_view(),name="dashboard"),
    path('',include(product_router.urls)),
    path('',include(router.urls)),
    
  ]  
#     path('products/',views.ProductList.as_view(),name='adminProductList'),
#     path('products/<int:pk>',views.ProductDetail.as_view(),name='adminProductDetail'),
#     path(),
#     path(),