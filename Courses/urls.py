from django.urls import path
from .views import CourseCreateView,CourseDeleteView,CourseListView,CourseUpdateView

urlpatterns = [
    path('courses/',CourseListView.as_view(),name='course-list'),
    path('course/create/',CourseCreateView.as_view(),name='course-create'),
    path('courses/<int:pk>/update/',CourseUpdateView.as_view(),name='course-upate'),
    path('course/<int:pk>/delete/',CourseDeleteView.as_view(),name='course-delete'),
     
]
