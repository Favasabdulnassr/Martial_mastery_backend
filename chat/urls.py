from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet,StudentDetailView,TutorDetailView

router = DefaultRouter()
router.register(r'chats',ChatViewSet,basename='chat')

urlpatterns = [
    path('api/',include(router.urls)),
    path('students/<int:id>/', StudentDetailView.as_view(), name='student-detail'),
    path('tutor/<int:id>/', TutorDetailView.as_view(), name='student-detail'),


]
