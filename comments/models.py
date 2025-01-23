from django.db import models
from django.utils import timezone
from payment.models import PurchasedCourseLesson
from user_auth.models import CustomUser
# Create your models here.

class LessonComment(models.Model):
    lesson = models.ForeignKey(PurchasedCourseLesson,on_delete=models.CASCADE,related_name='comments')
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(CustomUser,related_name='liked_comments',blank=True)
    parent = models.ForeignKey('self',null=True,blank=True,on_delete=models.CASCADE,related_name='replies')


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"comment by {self.user.email} on {self.lesson.title}"

    @property
    def is_reply(self):
        return self.parent is not None
    
    def get_replies(self):
        return self.replies.all()
    
    def like_count(self):
        return self.likes.count()




