from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(
        required=True,
        validators = [UniqueValidator(queryset=User.objects.all())]
    )
    phone_number = serializers.CharField(
        required = True,
        validators = [UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)  
    
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        default=User.DEFAULT_ROLE,  
        required=False  
    )

    experience = serializers.CharField(required=False, allow_blank=True) 
    bio = serializers.CharField(required=False, allow_blank=True)  


    class Meta:
        model = User
        fields = ('first_name','email','phone_number','password', 'confirm_password','role','experience','bio')


    def validate(self,data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Password do not match')
        return data
    
    def create(self,validated_data):
        validated_data.pop('confirm_password')  

        user = User.objects.create_user(**validated_data)
        return user



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    @classmethod
    def get_token(cls,user):
#Generates the token
        token = super().get_token(user)
        token['first_name'] = user.first_name
        token['email'] = user.email
        token['role'] = user.role
        token['phone_number'] = user.phone_number
        token['last_name'] = user.last_name
        token['profile'] = user.profile
        token['experience'] = user.experience
        token['bio'] = user.bio

         # If user has a profile image, get the URL of the image.
        if user.profile:
            # Assuming `profile` is an ImageField in the `User` model
            token['profile'] = user.profile.url if user.profile else None
        else:
            token['profile'] = None

        return token
        
        



class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name','last_name','email','phone_number','profile','experience','bio') 

    def validate_first_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("First name should only contain letters.")
        if len(value) < 3:
            raise serializers.ValidationError("First name must be at least 2 characters long.")
        return value

    def validate_last_name(self, value):
        if value and not value.isalpha():
            raise serializers.ValidationError("Last name should only contain letters.")
        return value

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        if len(value) != 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits.")
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        return value          



from .models import CustomUser
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = fields = ['id', 'email', 'first_name', 'last_name', 'phone_number']
    
        
            