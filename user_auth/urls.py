from django.urls import path
from .views import RegisterView,ProfileUpdateView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairView,VerifyOtpView,ProfilePictureView,UserListView,TutorRegister,TutorListView,ChangePassword

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('verify/',VerifyOtpView.as_view(),name='verify'),
    path('profile/update/',ProfileUpdateView.as_view(),name='profile-update'),
    path('profile/profile_picture/',ProfilePictureView.as_view(),name='profile_picture'),
    path('tutor/register/',TutorRegister.as_view(),name='tutor_register'),
    path('users/',UserListView.as_view(),name='users'),
    path('tutors/',TutorListView.as_view(),name='tutors'),
    path('change_password/',ChangePassword.as_view(),name='change_password'),
    # Jwt Token Urls

    path('token/',MyTokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


