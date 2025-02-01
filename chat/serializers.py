from rest_framework import serializers
from .models import ChatMessage,ChatRoom

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.CharField(source='sender.email',read_only=True)
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = ['id','content','timestamp','sender_email','sender_name','is_read']


        def get_sender_name(self,obj):
            return f"{obj.sender.first_name}"
        

class ChatRoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    other_user = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id','other_user','last_message','created_at']


    def get_last_message(self,obj):
        last_message = obj.messages.last()

        if last_message:
            return ChatMessageSerializer(last_message).data
        return None

    def get_other_user(self,obj):
        request_user = self.context['request'].user
        other_user = obj.student if request_user == obj.tutor else obj.tutor
        return {
            'id': other_user.id,
            'email':other_user.email,
            'name':f"{other_user.first_name}"
        }
    

from rest_framework import serializers
from .models import CustomUser

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'phone_number', 'first_name', 'last_name',  'profile']
