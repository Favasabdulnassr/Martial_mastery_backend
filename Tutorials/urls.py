from django.urls import path
from .views import TutorialViewSet,VideoUploadView

tutorial_create = TutorialViewSet.as_view({'post':'create'})
tutorial_list  = TutorialViewSet.as_view({'get':'list'})
tutorial_detail = TutorialViewSet.as_view({'get':'retrieve_detail'})

urlpatterns = [
    path('create/',tutorial_create,name='create'),
    path('list/<int:tutor_id>/',tutorial_list,name='list'),
    path('tutorial/<int:pk>/',tutorial_detail,name='retrieve_tutorial'),
    path('tutorial/<int:tutorial_id>/upload_video/', VideoUploadView.as_view(), name='upload_video'),
]



