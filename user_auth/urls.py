from django.urls import path
from .views import RegisterView,ProfileUpdateView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairView,VerifyOtpView,ProfilePictureView,ResendOtpView
from .views import UserListView,TutorRegister,TutorListView,ChangePassword,GoogleSignInView,ForgotPasswordView,ResetPasswordView,tutor_students

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('resend-otp/',ResendOtpView.as_view(),name='resend-otp'),
    path('verify-otp/',VerifyOtpView.as_view(),name='verify-otp'),
    path('profile/',ProfileUpdateView.as_view(),name='profile-update'),
    path('profile/picture/',ProfilePictureView.as_view(),name='profile-picture'),
    path('tutors/register/',TutorRegister.as_view(),name='tutor-register'),
    path('users/',UserListView.as_view(),name='users'),
    path('tutors/',TutorListView.as_view(),name='tutors'),
    path('tutor/students/',tutor_students, name='tutor-students'),

    path('change-password/',ChangePassword.as_view(),name='change-password'),
    # Jwt Token Urls

    path('token/',MyTokenObtainPairView.as_view(),name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('google/login/', GoogleSignInView.as_view(), name='google-login'),
    path('forgot-password/',ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<str:token>/',ResetPasswordView.as_view(), name='reset-password'),


]


