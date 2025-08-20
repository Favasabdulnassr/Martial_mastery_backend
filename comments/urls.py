from django.urls import path
from .views import manage_comment,create_comment,get_lesson_comments

urlpatterns = [
    path('lessons/<int:lesson_id>/',get_lesson_comments,name='lesson-comments'),
    path('lessons/<int:lesson_id>/create/',create_comment,name='lesson-comment-create'),
    path('<int:comment_id>/', manage_comment, name='comment-detail'),


]

