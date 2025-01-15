from django.urls import path
from .views import InitiatePaymentAPIView,PurchasedCoursesView, PurchasedCourseLessonListView

urlpatterns = [
    path('purchase/<int:course_id>/', InitiatePaymentAPIView.as_view(), name='payment-purchase'),
    path('purchased-courses/', PurchasedCoursesView.as_view(), name='purchased_courses'),
    path('purchased-courses/<int:course_id>/lessons/',  PurchasedCourseLessonListView.as_view(), name='purchased_lessons'),


]
