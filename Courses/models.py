from django.db import models
from user_auth.models import CustomUser

# Create your models here.

class Course(models.Model):
    name = models.CharField(max_length=100,unique=True)
    description = models.TextField()
    tutor = models.ManyToManyField(CustomUser,related_name="courses",blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
