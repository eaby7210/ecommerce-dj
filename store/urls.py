from django.urls import path
from . import views


# URLConf
urlpatterns = [
    path('products/', views.ProductListView.as_view(),name='product_list'),
    # path('products/<int:pk>/',views.product_detail,name='product_detail'),
    # path('collection/<int:pk>/',views.CollectionDetails.as_view(),name='collection_list'),
    path('collection/',views.CollectionListView.as_view(),name='collection_list'),
    # path('customers/',views.CustomerViewSet.as_view())
]
