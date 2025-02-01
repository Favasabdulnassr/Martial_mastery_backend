from django.db import models
from user_auth.models import CustomUser


class ChatRoom(models.Model):
    tutor = models.ForeignKey(CustomUser, related_name='tutor_chats', on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, related_name='student_chats', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['tutor', 'student']

    def __str__(self):
        return f"Chat between {self.tutor.email} and {self.student.email}"
    



class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']