from django.urls import path
from .views import PaymentViewSet,PurchasedCoursesView, PurchasedCourseLessonListView
from .views import stripe_webhook,PurchasedCourseLessonDetailView,PurchasedCourseByTutorView
from .views import TutorPurchasedCourseLessonListView,TutorPurchasedCourseLessonDetailView,TutorStudentsListView


urlpatterns = [
    path('courses/<int:pk>/initiate/', PaymentViewSet.as_view({'post': 'initiate'}), name='payment-initiate'),
    path('webhook/', stripe_webhook, name='stripe-webhook'),

    path('courses/', PurchasedCoursesView.as_view(), name='purchased-courses'),
    path('courses/<int:course_id>/lessons/',  PurchasedCourseLessonListView.as_view(), name='purchased-lessons'),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/',PurchasedCourseLessonDetailView.as_view(),name='purchased-lesson-detail'),

    path('tutors/me/purchased-courses/', PurchasedCourseByTutorView.as_view(), name='purchased-courses-by-tutor'),
    path('tutors/me/courses/<int:course_id>/lessons/', TutorPurchasedCourseLessonListView.as_view(), name='tutor-purchased-lessons'),
    path('tutors/me/courses/<int:course_id>/lessons/<int:lesson_id>/',TutorPurchasedCourseLessonDetailView.as_view(),name='tutor-purchased-lesson-detail'),
    path('tutors/<int:tutor_id>/students/', TutorStudentsListView.as_view(), name='tutor-students'),

]
