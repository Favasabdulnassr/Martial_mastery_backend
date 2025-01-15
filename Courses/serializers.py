from rest_framework import serializers
from .models import Course,CourseLesson
from user_auth.serializers import CustomUserSerializer





class CourseLessonSerializer(serializers.ModelSerializer):
    cloudinary_url = serializers.SerializerMethodField()



    class Meta:
        model = CourseLesson
        fields = ['id','title','description','cloudinary_url','thumbnail','order','created_at']
        read_only_fields = ['order']

    def validate(self, data):
    # Ensure required fields are present
        if not data.get('title'):
            raise serializers.ValidationError({"title": "Title is required"})
        if not data.get('description'):
            raise serializers.ValidationError({"description": "Description is required"})
        if not data.get('cloudinary_url'):
            raise serializers.ValidationError({"cloudinary_url": "Video URL is required"})
        return data
    

    def get_cloudinary_url(self, obj):
        return obj.get_video_url()



class CourseSerialzer(serializers.ModelSerializer):
    tutor = CustomUserSerializer()
    tutorials = CourseLessonSerializer(many=True,read_only=True)

    class Meta:
        model = Course
        fields = ['id','title','description','tutor','duration_weeks','fees','status','completed','created_at','updated_at','tutorials']
        read_only_fields = ['status','completed','tutor']



class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'duration_weeks', 'fees','tutor']
