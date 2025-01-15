from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator
from cloudinary.models import CloudinaryField
from user_auth.models import CustomUser
from django.conf import settings




class CourseManager (models.Manager):
    def approved(self):
        return self.filter(status='approved')
    
    def completed(self):
        return self.filter(completed=True)
        

class Course(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    )
    
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField()
    tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_courses')
    duration_weeks = models.PositiveIntegerField(validators=[MinValueValidator(1)],default=1)
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    completed = models.BooleanField(default=False) 

    
    objects = CourseManager() 
  
    def __str__(self):
        return f"{self.title} by {self.tutor.email}"
    


class CourseLesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='tutorials')
    title = models.CharField(max_length=200)  # Tutorial title
    description = models.TextField(max_length=200)  # Tutorial description
    cloudinary_url = CloudinaryField('video', resource_type='video')   # Video resource from Cloudinary
    thumbnail = models.ImageField(upload_to='video_thumbnails/', null=True, blank=True)  # Local thumbnail
    order = models.PositiveIntegerField(unique=True)  # To define the sequence of tutorials
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  

    class Meta:
        ordering = ['order']  # Tutorials are ordered by the 'order' field

    def get_video_url(self):
        if hasattr(self.cloudinary_url, 'url'):
            return self.cloudinary_url.url
        return str(self.cloudinary_url)    
        
    def __str__(self):
            return f"{self.title} - {self.course.title}"    
    






