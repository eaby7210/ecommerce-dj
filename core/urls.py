from django.urls import path,include
from .views import *
from django.urls import include
from rest_framework.routers import DefaultRouter
import pprint

# router=DefaultRouter()
# router.register(r'users',UserViewSet,basename='user')
# pprint.pprint(router.urls)

# URLConf
urlpatterns = [
    # path('',include(router.urls)),
    path('', HomePageView.as_view(),name="home"),
    path('signup/',SignupAPIView.as_view(),name="signup"),
    path('login/',LoginAPIView.as_view(),name="login"),
    path('logout/',LogoutAPIView.as_view(),name="logout"),
    path('profile/',ProfileAPIView.as_view(),name="profile"),
]
