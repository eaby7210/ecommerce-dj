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
router.register('order',views.OrderViewSet,basename='admin-order')
router.register('coupon',views.CouponViewSet,basename="admin-coupon")


product_router=routers.NestedSimpleRouter(router,'products',lookup='product')
product_router.register('images',views.ProductImageViewSet,basename='product_images')



urlpatterns=[
    path('',views.Dashboard.as_view(),name="dashboard"),
    path('',include(product_router.urls)),
    path('',include(router.urls)),
    path('nav-updates',views.NavUpdateView.as_view(),name="nav-update"),
    path('sales-report/',views.SalesReportView.as_view(),name='sales-report')

    
  ]  
#     path('products/',views.ProductList.as_view(),name='adminProductList'),
#     path('products/<int:pk>',views.ProductDetail.as_view(),name='adminProductDetail'),
#     path(),
#     path(),
