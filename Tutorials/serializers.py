from rest_framework import serializers
from .models import Course, Tutorial, Video
from user_auth.models import CustomUser

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id','tutorial','title','video_file','order','is_active','created_at']



class TutorialSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)  # Nested VideoSerializer

    class Meta:
        model = Tutorial
        fields = ['id','course','tutor','title','description','created_at','videos']

