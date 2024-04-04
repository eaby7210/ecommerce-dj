from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('products/', views.product_list),
    path('products/<int:pk>/',views.product_detail),
    path('collection/<int:pk>/',views.CollectionPage.as_view(),name='collection_page'),
    path('collection',views.collection_list)
]
