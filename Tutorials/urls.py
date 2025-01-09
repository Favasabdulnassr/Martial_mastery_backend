from django.urls import path
from .views import TutorialViewSet,VideoUploadView,TutorStudentsViewSet,DeleteTutorialView,DeleteVideoView

tutorial_create = TutorialViewSet.as_view({'post':'create'})
tutorial_list  = TutorialViewSet.as_view({'get':'list'})
tutorial_detail = TutorialViewSet.as_view({'get':'retrieve_detail'})
tutorial_videos = TutorialViewSet.as_view({'get':'get_videos'})
tutor_students_list = TutorStudentsViewSet.as_view({'get': 'list'})


urlpatterns = [
    path('create/',tutorial_create,name='create'),
    path('list/<int:tutor_id>/',tutorial_list,name='list'),
    path('tutorial/<int:pk>/',tutorial_detail,name='retrieve_tutorial'),
    path('tutorial/<int:tutorial_id>/upload_video/', VideoUploadView.as_view(), name='upload_video'),
    path('tutorial/<int:pk>/videos/',tutorial_videos,name='tutorial_videos'),
    path('tutor/students/', tutor_students_list, name='tutor-students-list'),
    path('delete-tutorial/<int:tutorial_id>/', DeleteTutorialView.as_view(), name='delete-tutorial'),
    path('delete-video/<int:video_id>/', DeleteVideoView.as_view(), name='delete-video'),

]



