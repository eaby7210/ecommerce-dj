from django.urls import path
from django.urls.conf import include
from . import views
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register('products',views.ProductViewSet)
router.register('collections',views.CollectionViewSet)
# print(router.urls)


urlpatterns=[
    path('',include(router.urls)),
#     path('products/',views.ProductList.as_view(),name='adminProductList'),
#     path('products/<int:pk>',views.ProductDetail.as_view(),name='adminProductDetail'),
#     path(),
#     path(),
]