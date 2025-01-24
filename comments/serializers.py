from rest_framework import serializers
from .models import LessonComment


class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value,context=self.context)
        return serializer.data


from django.utils.timesince import timesince
from django.utils.timezone import now

class LessonCommentSerializer(serializers.ModelSerializer):
    replies = RecursiveSerializer(many=True,read_only=True)
    user = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()  



    class Meta:
        model = LessonComment
        fields = [
            'id',
            'lesson',
            'user',
            'content',
            'created_at',
            'updated_at',
            'replies',
            'time_ago'
        ]
        read_only_fields = ['user','created_at','updated_at']

    def get_user(self,obj):
        user = obj.user
        return {
            "id": user.id,
            "name": user.first_name ,
            "profile":user.profile.url,
        }
    
    def get_time_ago(self, obj):
        # Calculate relative time using timesince
        return f"{timesince(obj.created_at, now())} ago"


