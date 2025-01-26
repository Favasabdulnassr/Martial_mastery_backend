from django.urls import path
from .views import PaymentViewSet,PurchasedCoursesView, PurchasedCourseLessonListView
from .views import stripe_webhook,PurchasedCourseLessonDetailView,PurchasedCourseByTutorView
from .views import TutorPurchasedCourseLessonListView,TutorPurchasedCourseLessonDetailView


urlpatterns = [
    path('purchase/<int:pk>/', PaymentViewSet.as_view({'post': 'initiate'}), name='payment-purchase'),
    path('purchased-courses/', PurchasedCoursesView.as_view(), name='purchased_courses'),
    path('purchased-courses/<int:course_id>/lessons/',  PurchasedCourseLessonListView.as_view(), name='purchased_lessons'),
    path('webhook/', stripe_webhook, name='stripe-webhook'),
    path('purchased-course/<int:course_id>/lesson/<int:lesson_id>/',PurchasedCourseLessonDetailView.as_view(),name='purchased_lesson_detail'),
    path('tutor-purchased-course/<int:course_id>/lesson/<int:lesson_id>/',TutorPurchasedCourseLessonDetailView.as_view(),name='tutor_purchased_lesson_detail'),

    path('tutor/purchased-courses/', PurchasedCourseByTutorView.as_view(), name='purchased-courses-by-tutor'),
    path('tutor/courses/<int:course_id>/lessons/', TutorPurchasedCourseLessonListView.as_view(), name='tutor-purchased-course-lessons'),

]
