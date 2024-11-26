from django.urls import path
from .views import RegisterView,ProfileUpdateView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairView,VerifyOtpView

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('verify/',VerifyOtpView.as_view(),name='verify'),
    path('profile/update/',ProfileUpdateView.as_view(),name='profile-update'),

    # Jwt Token Urls

    path('token/',MyTokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


