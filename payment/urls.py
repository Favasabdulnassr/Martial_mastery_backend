from django.urls import path
from .views import PaymentViewSet,PurchasedCoursesView, PurchasedCourseLessonListView
from .views import stripe_webhook,PurchasedCourseLessonDetailView

urlpatterns = [
    path('purchase/<int:pk>/', PaymentViewSet.as_view({'post': 'initiate'}), name='payment-purchase'),
    path('purchased-courses/', PurchasedCoursesView.as_view(), name='purchased_courses'),
    path('purchased-courses/<int:course_id>/lessons/',  PurchasedCourseLessonListView.as_view(), name='purchased_lessons'),
    path('webhook/', stripe_webhook, name='stripe-webhook'),
    path('purchased-course/<int:course_id>/lesson/<int:lesson_id>/',PurchasedCourseLessonDetailView.as_view(),name='purchased_lesson_detail')



]
