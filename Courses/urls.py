from django.urls import path
from .views import CourseViewSet,LessonUploadView,LessonViewSet,CourseViewAdmin
from .views import CourseStatusUpdateView,CourseViewUser,CourseLessonView,UpdateCourseView


course_create = CourseViewSet.as_view({'get':'list','post':'create'})
course_update =  CourseViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})
course_completed = CourseViewSet.as_view({'put': 'mark_as_completed'})
Lessons_create = LessonViewSet.as_view({'get': 'list'})
Lessons_update = LessonViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})


course_admin_completed = CourseViewAdmin.as_view({'get': 'completed'})  #
admin_course_detail = CourseViewAdmin.as_view({'get': 'completed_course'})

urlpatterns = [
    path('courses/',course_create, name='course-list-create'), 
    path('courses/<int:pk>/',course_update, name='course-detail'), 
    path('courses/<int:pk>/update/', UpdateCourseView.as_view(), name='course-update'),

    path('courses/<int:pk>/completion/',course_completed, name='course-completion'),
    path('courses/<int:pk>/status/', CourseStatusUpdateView.as_view(), name='course-update-status'),

    path('courses/<int:course_id>/lessons/', Lessons_create, name='lesson-list-create'),
    path('courses/<int:course_id>/lessons/<int:pk>/', Lessons_update, name='lesson-detail'), 
    path('courses/<int:courses_id>/lessons/upload/', LessonUploadView.as_view(), name='lesson-upload'),

    path('users/completed-courses/', CourseViewUser.as_view(), name='user-completed-courses'),

    path('admins/courses/completed/', course_admin_completed, name='admin-course-completed'),  
    path('admins/courses/<int:pk>/completed/',admin_course_detail,name='course_detail_admin'),   
    path('courses/<int:course_id>/lessons/', CourseLessonView.as_view(), name='course-lessons'),
    

]
