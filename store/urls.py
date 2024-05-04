from django.urls import path
from django.urls.conf import include
from . import views
from rest_framework.routers import SimpleRouter

router=SimpleRouter()
router.register('brands',views.BrandViewSet,basename="u-brand")
router.register('category',views.CategoryViewSet,basename='u-category')
router.register('cart',views.CartViewSet,basename='u-cart')


# URLConf
urlpatterns = [
    path('products/', views.ProductListView.as_view(),name='product_list'),
    path('products/<int:pk>/',views.ProductDetailView.as_view(),name='product_page'),
    path('',include(router.urls)),
    # path('collection/<int:pk>/',views.CollectionDetails.as_view(),name='collection_list'),
    # path('customers/',views.CustomerViewSet.as_view())
]
