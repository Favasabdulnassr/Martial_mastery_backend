from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Course,Tutorial,Video
from .serializers import TutorialSerializer,VideoSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status


# Create your views here.


class TutorialViewSet(viewsets.ModelViewSet):
    serializer_class = TutorialSerializer
    permission_classes = [IsAuthenticated]



    
    def get_queryset(self):

    # This method is overridden to return only the tutorials belonging to the logged-in tutor.

        tutor = self.request.user
        if tutor.role != 'tutor':
            raise PermissionError("Only tutors can access their tutorials.")
        
        tutorials = Tutorial.objects.filter(tutor=tutor).prefetch_related('videos')

        tutorial_data = []

        # Debug: Print tutorials and associated videos
        for tutorial in tutorials:
            print(tutorial)
            tutorial_info = {
                'id':tutorial.id,
                'course':tutorial.course,
                'tutor':tutorial.tutor,
                'title':tutorial.title,
                'description': tutorial.description,
                'videos':[]

            }

            for video in tutorial.videos.all():
                video_info = {
                    'id':video.id,
                    'tutorial':video.tutorial,
                    'title':video.title,
                    'video_file':video.video_file,
                    'order':video.order,
                    'is_active':video.is_active,
                }   

                tutorial_info['videos'].append(video_info) 

            tutorial_data.append(tutorial_info)    

           
        
        return tutorial_data  # Ensure you're returning the correct queryset


    def perform_create(self, serializer):
        tutor = self.request.user
        if tutor.role != 'tutor':
            print('AAAAAAAAAAAAAaaala',tutor)
            raise PermissionError("Only tutor can create tutorials")
        
        serializer.save(tutor=tutor)


    @action(detail=True,methods=['get'])
    def retrieve_detail(self,request,pk=None):
        try:
            print('mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm')
            tutorial = Tutorial.objects.get(id=pk)
            serializer = TutorialSerializer(tutorial)
            return Response(serializer.data)
        
        except Tutorial.DoesNotExist:
            print('iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
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
            video_file=video_file,
            order=request.data.get('order'),
            is_active=is_active
        )
        video.save()

        return Response({'message': 'Video uploaded successfully'}, status=status.HTTP_201_CREATED)