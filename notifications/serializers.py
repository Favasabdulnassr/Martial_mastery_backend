from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'created_at', 'read', 'course', 'course_title']
    
    def get_course_title(self, obj):
        if obj.course:
            return obj.course.title
        return None