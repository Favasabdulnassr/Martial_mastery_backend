from rest_framework import serializers
from .models import LessonComment


class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value,context=self.context)
        return serializer.data


class LessonCommentSerializer(serializers.ModelSerializer):
    replies = RecursiveSerializer(many=True,read_only=True)
    user_email = serializers.SerializerMethodField()
    likes_count =  serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = LessonComment
        fields = [
            'id',
            'lesson',
            'user',
            'user_email',
            'content',
            'created_at',
            'updated_at',
            'likes_count',
            'is_liked_by_user',
            'replies',
        ]
        read_only_fields = ['user','created_at','updated_at']

    def get_user_email(self,obj):
        return obj.user.email
    
    def get_likes_count(self,obj):
        return obj.likes.count()
    
    def get_is_liked_by_user(self,obj):
        request = self.context.get('request')
        if request and hasattr(request,'user') and request.user.is_authenticated:
            return obj.likes.filter(id = request.user.id).exists()
        
        return False

