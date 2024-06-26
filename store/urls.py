from django.urls import path
from django.urls.conf import include
from . import views
from rest_framework.routers import SimpleRouter

router=SimpleRouter()
router.register('product',views.ProductViewset,basename="u-product")
router.register('brands',views.BrandViewSet,basename="u-brand")
router.register('category',views.CategoryViewSet,basename='u-category')
router.register('cart',views.CartViewSet,basename='u-cart')
router.register('order',views.OrderViewSet,basename='u-order')
router.register('wishlist',views.WhishListViewSet,basename='u-wishlist')
router.register('transactions', views.TransactionViewSet, basename='u-transaction')


# URLConf
urlpatterns = [
    
    path('checkout/',views.CheckoutView.as_view(),name='checkout'),
    path('couponcheck/',views.CheckCoupon.as_view(),name='coupon-check'),
    path('payment/',views.payment,name="u-payment"),
    path('',include(router.urls)),
    # path('collection/<int:pk>/',views.CollectionDetails.as_view(),name='collection_list'),
    # path('customers/',views.CustomerViewSet.as_view())
]
