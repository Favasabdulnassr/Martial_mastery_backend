from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin



class CustomUserManager(BaseUserManager):
    def create_user(self,email,phone_number,password=None,**extra_fields):
        if not email:
            raise ValueError("The email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email,phone_number=phone_number,password=password,**extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self,email,phone_number,password=None,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)

        return self.create_user(email,phone_number,password,**extra_fields)    
    

class CustomUser(AbstractBaseUser,PermissionsMixin):

    ROLE_CHOICES = (
        ('student','Student'),
        ('tutor','Tutor'),
        ('admin','Admin')
    )
    DEFAULT_ROLE = 'student'

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15,unique=True)
    first_name = models.CharField(max_length=30,blank=True)
    last_name = models.CharField(max_length=30,blank=True)
    status = models.BooleanField(default=True)
    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default=DEFAULT_ROLE)
    is_staff = models.BooleanField(default=False)
    profile = models.ImageField(upload_to='userProfiles',null=True,blank=True)


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self):
        return self.email