from django.urls import path
from .views import manage_comment,create_comment,get_lesson_comments,toggle_like_comment

urlpatterns = [
    path('get-comments/<int:lesson_id>/',get_lesson_comments,name='get-comments'),
    path('create/<int:lesson_id>/',create_comment,name='create-comment'),
    path('manage/<int:comment_id>/', manage_comment, name='manage-comment'),
    path('toggle-like/<int:comment_id>/', toggle_like_comment, name='toggle-like-comment'),

    
]

