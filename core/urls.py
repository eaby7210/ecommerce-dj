from django.urls import path,include
from .views import *
from django.urls import include
from rest_framework.routers import SimpleRouter
import pprint

router=SimpleRouter()
router.register(r'address',AddressViewSet,basename='u-address')


# URLConf
urlpatterns = [
    path('', HomePageView.as_view(),name="home"),
    path('',include(router.urls)),
    path('signup/',SignupAPIView.as_view(),name="signup"),
    path('login/',LoginAPIView.as_view(),name="login"),
    path('logout/',LogoutAPIView.as_view(),name="logout"),
    path('profile/',ProfileAPIView.as_view(),name="profile"),
    path('emailverify/<int:user_id>/',VerifyEmailView.as_view(),name="verify-email"),
    path('resendmail/<int:user_id>/',ResendEmailView.as_view(),name="resendmail")
]
