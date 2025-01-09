from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Course,Tutorial,Video
from .serializers import TutorialSerializer,VideoSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from user_auth.models import CustomUser
from TutorialPayment.models import TutorialAccess

from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Q




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Tutorial, Video
from rest_framework.permissions import IsAuthenticated

class DeleteTutorialView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, tutorial_id):
        try:
            tutorial = Tutorial.objects.get(id=tutorial_id, tutor=request.user)
            tutorial.delete()
            return Response({"message": "Tutorial deleted successfully"}, status=status.HTTP_200_OK)
        except Tutorial.DoesNotExist:
            return Response({"error": "Tutorial not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DeleteVideoView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id, tutorial__tutor=request.user)
            video.delete()
            return Response({"message": "Video deleted successfully"}, status=status.HTTP_200_OK)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TutorStudentsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        tutor = request.user
        search_query = request.query_params.get('search', '')
        
        # Get all tutorial IDs for this tutor
        tutorial_ids = Tutorial.objects.filter(tutor=tutor).values_list('id', flat=True)
        
        # Get all students who have access to these tutorials
        students = CustomUser.objects.filter(
            Q(tutorialaccess__tutorial_id__in=tutorial_ids) & 
            Q(role='student')
        ).distinct()

        # Apply search if provided
        if search_query:
            students = students.filter(
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(phone_number__icontains=search_query)
            )

        # Basic pagination
        page = int(request.query_params.get('page', 1))
        per_page = 10
        start = (page - 1) * per_page
        end = start + per_page

        total_count = students.count()
        students = students[start:end]

        return Response({
            'students': [{
                'id': student.id,
                'email': student.email,
                'first_name': student.first_name,
                'phone_number': student.phone_number,
                'purchased_tutorials': TutorialAccess.objects.filter(
                    user=student,
                    tutorial__tutor=tutor
                ).count()
            } for student in students],
            'total_count': total_count,
            'has_next': (start + per_page) < total_count,
            'has_previous': page > 1
        })



class TutorialViewSet(viewsets.ModelViewSet):
    serializer_class = TutorialSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tutor = self.request.user
        if tutor.role != 'tutor':
            raise PermissionDenied("Only tutors can access their tutorials.")
        
        # Fetch the tutorials belonging to the logged-in tutor
        return Tutorial.objects.filter(tutor=tutor).prefetch_related('videos')
    
    @action(detail=True,methods=['get'],url_path='videos')
    def get_videos(self,request,pk=None):
        try:
            tutorial = Tutorial.objects.prefetch_related('videos').get(id=pk)


            serializer = TutorialSerializer(tutorial)
            return Response(serializer.data,status=status.HTTP_200_OK)
        
        except Tutorial.DoesNotExist:
            return Response({'error':'Tutorial not found'},status=status.HTTP_404_NOT_FOUND)
        



    def perform_create(self, serializer):
        tutor = self.request.user
        if tutor.role != 'tutor':
            raise PermissionError("Only tutor can create tutorials")
        
        serializer.save(tutor=tutor)


    @action(detail=True,methods=['get'])
    def retrieve_detail(self,request,pk=None):
        try:
            tutorial = Tutorial.objects.get(id=pk)
            serializer = TutorialSerializer(tutorial)
            return Response(serializer.data)
        
        except Tutorial.DoesNotExist:
            return Response({'error':'Tutorial not found'},status=404)
        








class VideoUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, tutorial_id, *args, **kwargs):
        tutor = request.user
        if tutor.role != 'tutor':
            return Response({"detail": "Only tutors can upload videos."}, status=status)

        tutorial = Tutorial.objects.get(id=tutorial_id)
        if not tutorial:
            return Response({"detail": "Tutorial not found."}, status=status.HTTP_404_NOT_FOUND)

        video_file = request.FILES.get('video_file')
        thumbnail_file = request.FILES.get('thumbnail')  # Get thumbnail file

        if not video_file:
            return Response({"detail": "No video file provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        is_active = request.data.get('is_active', 'true')  # default to 'true' if not provided

        if is_active == 'true':
            is_active = True
        elif is_active == 'false':
            is_active = False

        video = Video.objects.create(
            tutorial=tutorial,
            title=request.data.get('title'),
            cloudinary_url = video_file,
            thumbnail=thumbnail_file, 
            order=request.data.get('order'),
            is_active=is_active
        )
        video.save()

        return Response({'message': 'Video uploaded successfully'}, status=status.HTTP_201_CREATED)