from django.urls import path
from .views import CourseViewSet,LessonUploadView,LessonViewSet,CourseViewAdmin
from .views import CourseStatusUpdateView,CourseViewUser,CourseLessonView


course_create = CourseViewSet.as_view({'get':'list','post':'create'})
course_update =  CourseViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})
course_completed = CourseViewSet.as_view({'put': 'mark_as_completed'})
Lessons_create = LessonViewSet.as_view({'get': 'list'})
Lessons_update = LessonViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})


course_admin_completed = CourseViewAdmin.as_view({'get': 'completed'})  # List of completed courses
admin_course_detail = CourseViewAdmin.as_view({'get': 'completed_course'})

urlpatterns = [
    path('course/',course_create, name='course-list-create'),
    path('course/<int:pk>/',course_update, name='course-detail'),
    path('course/<int:pk>/mark_as_completed/',course_completed, name='course-mark-as-completed'),
    path('course/<int:course_pk>/lesson/', Lessons_create, name='lesson-list-create'),
    path('course/<int:course_pk>/lesson/<int:pk>/', Lessons_update, name='lesson-detail'),
    path('course/<int:CourseId>/upload_lesson/', LessonUploadView.as_view(), name='upload_video'),


      # Admin-specific routes
    path('course/completed/', course_admin_completed, name='admin-course-completed'),  
    path('course/<int:pk>/completed/',admin_course_detail,name='course_detail_admin'),

    path('course/<int:pk>/update_status/', CourseStatusUpdateView.as_view(), name='course-update-status'),
    path('user/completed-courses/', CourseViewUser.as_view(), name='user-completed-courses'),
    path('course/<int:course_id>/lessons/', CourseLessonView.as_view(), name='course-lessons'),






    
   
]
