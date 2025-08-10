from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response   
from rest_framework import viewsets,permissions,status
from django.db.models import Q
from .serializers import ChatMessageSerializer,ChatRoomSerializer
from .models import ChatMessage,ChatRoom
from payment.models import PurchasedCourseUser

class ChatViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class  = ChatRoomSerializer

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(Q(tutor=user)|Q(student=user))
    

    @action(detail=False,methods=['POST'])
    def create_or_get_room(self,request):
        student_id = request.data.get('student_id')
        tutor_id = request.data.get('tutor_id')

        

        # Verify that the student has purchased a course from this tutor
        has_purchased = PurchasedCourseUser.objects.filter(
            user_id = student_id,
            purchased_course__tutor_id= tutor_id
        ).exists()



        if not has_purchased:
            return Response(
                {"error": "Student has not purchased any courses from this tutor"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        chat_room,created = ChatRoom.objects.get_or_create( 
            tutor_id = tutor_id,
            student_id  =student_id
        )

        serializer = self.get_serializer(chat_room)

        return Response(serializer.data)


    @action(detail=True,methods=['GET'])
    def messages(self,request,pk=None):
        chat_room=self.get_object()
        messages = chat_room.messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)    



from .models import CustomUser
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import StudentSerializer



class StudentDetailView(RetrieveAPIView):
    queryset = CustomUser.objects.filter(role='student')
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'  # Uses student ID for lookup

class TutorDetailView(RetrieveAPIView):
    queryset = CustomUser.objects.filter(role='tutor')
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'  # Uses student ID for lookup    