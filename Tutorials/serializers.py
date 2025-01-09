from rest_framework import serializers
from .models import Course, Tutorial, Video
from user_auth.models import CustomUser

class VideoSerializer(serializers.ModelSerializer):

    video_url = serializers.SerializerMethodField()
 
    class Meta:
        model = Video
        fields = ['id','tutorial','title','cloudinary_url','order','thumbnail','is_active','created_at','video_url']


    def get_video_url(sel,obj):
        return obj.get_video_url()



class TutorialSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)  # Nested VideoSerializer

    class Meta:
        model = Tutorial
        fields = ['id','course','tutor','title','description','price','created_at','videos']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be a non-negative value.")
        return value    

