from rest_framework import status,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .serializers import CourseSerialzer,CourseLessonSerializer,CourseCreateSerializer
from user_auth.permission import IsTutor,IsAdmin
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
import cloudinary
import cloudinary.uploader
from django.conf import settings
from .models import Course, CourseLesson
from django.db.models import Q
from user_auth.models import CustomUser




class CourseViewSet(viewsets.ModelViewSet):
    permission_classes =[IsAuthenticated,IsTutor]
    serializer_class = CourseSerialzer

    def get_queryset(self):
        return Course.objects.filter(tutor=self.request.user)
    

    
    def get_serializer_class(self):
        if self.action == 'create':
            return CourseCreateSerializer
        return CourseSerialzer



    @action(detail=True,methods=['put'])
    def mark_as_completed(self,request,pk=None):
        course = self.get_object()
        print(course)

        if not course.tutorials.exists():
            return Response(
                {"error":"cannot mark course as completed without any lessons"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if course.completed == True:
            course.completed = False
            course.status = 'pending'
            course.save()
            return Response({"message":"Course marked as a incompleted"},
                             status=status.HTTP_200_OK
                            )

        else:
            course.completed = True
            course.status = 'pending'
            course.save()
            return Response({"message":"Course marked as a completed"},
                             status=status.HTTP_200_OK
                            )

        
        
    
    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     if 'tutor' not in request.data:
    #         n = CustomUser.objects.filter(id=self.request.user.id)
    #         request.data['tutor'] = self.request.user

    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    
    #     if not serializer.is_valid():  # Check if the serializer is valid
    #         print("Validation Errors:", serializer.errors)  # Log the validation errors
    #         return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)  # Return the errors if invalid

    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)

    #     return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)
    




from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import Course
from .serializers import CourseUpdateSerializer
from user_auth.permission import IsTutor

class UpdateCourseView(APIView):
    permission_classes = [IsAuthenticated,IsTutor]  
    def get_object(self, pk):
        try:
            return Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            raise ValidationError("Course not found.")

    def put(self, request, pk, *args, **kwargs):
        course = self.get_object(pk)

        if course.tutor != request.user:
            return Response({"error": "You do not have permission to update this course."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()

        if 'tutor' not in data:
            data['tutor'] = request.user.id  

        serializer = CourseUpdateSerializer(course, data=data, partial=True)  # partial=True allows partial updates

        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)




class CourseViewAdmin(viewsets.ModelViewSet):
    permission_classes =[IsAuthenticated,IsAdmin]
    serializer_class = CourseSerialzer



    @action(detail=False, methods=['get'])
    def completed(self, request):
       
        search_query = request.query_params.get('search', '').strip()
        
        # Start with completed courses
        completed_courses = Course.objects.completed()
        
        # Apply search filter if search_query exists
        if search_query:
            completed_courses = completed_courses.filter(
                Q(title__icontains=search_query) |
                Q(tutor__first_name__icontains=search_query) |
                Q(tutor__last_name__icontains=search_query)
            ).distinct()
        
        serializer = self.get_serializer(completed_courses, many=True)
        return Response(serializer.data)

    

    @action(detail=True, methods=['get'])
    def completed_course(self, request, pk=None):
        """
        Custom action to fetch a single completed course by its ID
        """
        try:
            # Get the course by ID and check if it is completed
            course = Course.objects.get(id=pk, completed=True)
            serializer = self.get_serializer(course)
            return Response(serializer.data)
        except Course.DoesNotExist:
            raise PermissionDenied("You do not have permission to view this course")
        


class CourseStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, pk=None):
        try:
            course = Course.objects.get(id=pk)

            # Ensure the status provided is either 'approved' or 'rejected'
            status_to_update = request.data.get("status")

            if status_to_update not in ['approved', 'rejected']:
                return Response(
                    {"detail": "Invalid status. Status must be either 'approved' or 'rejected'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # If the status is 'rejected', set 'completed' to False
            if status_to_update == 'rejected':
                course.completed = False

            course.status = status_to_update
            course.save()

            return Response(
                {"message": f"Course status updated to {status_to_update}"},
                status=status.HTTP_200_OK
            )

        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    
    

class LessonViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsTutor]
    serializer_class = CourseLessonSerializer

    def get_queryset(self):
        return CourseLesson.objects.filter(course__tutor=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)
    
    





class LessonUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, CourseId, *args, **kwargs):
        try:
            # Configure Cloudinary with credentials
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
                api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
                api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
            )

            # Check if user is tutor
            tutor = request.user
            if tutor.role != 'tutor':
                return Response(
                    {"detail": "Only tutors can upload videos."}, 
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get course or return 404
            try:
                course = Course.objects.get(id=CourseId)
            except Course.DoesNotExist:
                return Response(
                    {"detail": "Course not found."}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Validate required fields
            video_file = request.FILES.get('video_file')
            thumbnail_file = request.FILES.get('thumbnail')
            title = request.data.get('title')
            description = request.data.get('description')
            order = request.data.get('order')

            if not all([video_file, title, description, order]):
                return Response({
                    "detail": "Missing required fields. Please provide video_file, title, description, and order."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Upload video to Cloudinary
            try:
                video_upload = cloudinary.uploader.upload(
                    video_file,
                    resource_type="video",
                    folder="course_videos/",
                    eager=[
                        {"streaming_profile": "full_hd", "format": "m3u8"}
                    ],
                    eager_async=True
                )
            except Exception as e:
                return Response({
                    "detail": f"Error uploading video to Cloudinary: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

          

            # # Create the lesson
            try:
                lesson = CourseLesson.objects.create(
                    course=course,
                    title=title,
                    description=description,
                    cloudinary_url=video_upload['secure_url'],  # Store only the public_id
                    thumbnail=thumbnail_file if thumbnail_file else None,
                    order=order
                )
            except Exception as e:
                return Response({
                    "detail": f"Error creating lesson: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Return successful response with sanitized data
            response_data = {
                'message': 'Lesson uploaded successfully',
                'lesson_id': lesson.id,
                'video_url': video_upload['secure_url'],  # Use the model method to get the URL
                'thumbnail_url': lesson.thumbnail.url if lesson.thumbnail else None
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "detail": f"Error processing request: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


from rest_framework.generics import ListAPIView

class CourseViewUser(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerialzer

    def get_queryset(self):
        return Course.objects.completed()
    




class CourseLessonView(ListAPIView):
    permission_classes = [IsAuthenticated]  # Optionally add permissions
    serializer_class = CourseLessonSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return CourseLesson.objects.filter(course_id=course_id)
