from django.db import models
from user_auth.models import CustomUser
from Courses.models import Course

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('purchase', 'Course Purchase'),
        ('message', 'New Message'),
        ('system', 'System Notification'),
    )
    
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.notification_type}: {self.title} for {self.recipient.email}" 