from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from payment.models import PurchasedCourseLesson
from .models import LessonComment
from .serializers import LessonCommentSerializer
from payment.models import PurchasedCourseUser



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request,lesson_id):
    lesson = get_object_or_404(PurchasedCourseLesson,id =lesson_id)
    user = request.user
    purchased_course = lesson.purchased_course

    is_tutor = purchased_course.tutor == user
    is_purchaser = PurchasedCourseUser.objects.filter(purchased_course=purchased_course, user=user).exists()

    if not (is_tutor or is_purchaser):
        return Response({'error': "You must purchase this course  to comments."},
                        status=status.HTTP_403_FORBIDDEN)
    
    
    parent_id = request.data.get('parent_id')
    content = request.data.get('content')

    if not content:
        return Response({"error": "Content is required"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    

    comment = LessonComment.objects.create(
        lesson=lesson,
        user=request.user,
        content=content,
        parent_id=parent_id
    )


    serializer = LessonCommentSerializer(comment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)








@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_lesson_comments(request,lesson_id):
    lesson = get_object_or_404(PurchasedCourseLesson,id=lesson_id)

    user = request.user
    purchased_course = lesson.purchased_course

    is_tutor = purchased_course.tutor == user
    is_purchaser = PurchasedCourseUser.objects.filter(purchased_course=purchased_course, user=user).exists()

    if not (is_tutor or is_purchaser):
        return Response({'error': "You must purchase this course or be the tutor to view comments."},
                        status=status.HTTP_403_FORBIDDEN)
    
    comments = LessonComment.objects.filter(lesson=lesson,parent=None)
    serializer = LessonCommentSerializer(comments,many=True,context={'request':request})
    return Response(serializer.data)




@api_view(['PUT','DELETE'])
@permission_classes([IsAuthenticated])
def manage_comment(request,comment_id):

    comment = get_object_or_404(LessonComment,id=comment_id)

    if comment.user != request.user:
        return Response({"error": "You don't have permission to modify this comment"}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    elif request.method == 'PUT':
        content = request.data.get('content')
        if not content:
            return Response({"error": "Content is required"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        comment.content = content
        comment.save()
        serializer = LessonCommentSerializer(comment)
        return Response(serializer.data)    