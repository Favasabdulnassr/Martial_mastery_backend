from django.db import models
from user_auth.models import CustomUser
from Courses.models import  Course
from cloudinary_storage.storage import VideoMediaCloudinaryStorage
from cloudinary_storage.validators import validate_video
from cloudinary.models import CloudinaryField
from django.conf import settings  # Import settings to access the cloud_name

# Create your models here.





class Tutorial(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='tutorials')
    tutor = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='tutors')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)  # Add price field
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title
    


class Video(models.Model):
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE, related_name="videos")
    title = models.CharField(max_length=200)
    cloudinary_url = CloudinaryField('video', resource_type='video')  # Specify resource_type as 'video'
    thumbnail = models.ImageField(upload_to='video_thumbnails/', null=True, blank=True)  # Thumbnail using local storage
    order = models.PositiveIntegerField()  # To define the sequence of videos
    is_active = models.BooleanField(default=True)  # To control which videos are accessible
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']


    def get_video_url(self):
        cloud_name = settings.CLOUDINARY_STORAGE['CLOUD_NAME']
        return f"https://res.cloudinary.com/{cloud_name}/video/upload/{self.cloudinary_url.public_id}.mp4"     

    def __str__(self):
        return self.title




