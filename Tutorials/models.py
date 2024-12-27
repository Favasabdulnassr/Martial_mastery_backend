from django.db import models
from user_auth.models import CustomUser
from Courses.models import  Course
# Create your models here.





class Tutorial(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='tutorials')
    tutor = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='tutors')
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    


class Video(models.Model):
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE, related_name="videos")
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='tutorial_videos/',null=True,blank=True)
    order = models.PositiveIntegerField()  # To define the sequence of videos
    is_active = models.BooleanField(default=True)  # To control which videos are accessible
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


