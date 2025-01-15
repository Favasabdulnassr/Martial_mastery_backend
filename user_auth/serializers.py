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
    confirm_password = serializers.CharField(write_only=True)  # Add confirm_password field
    
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        default=User.DEFAULT_ROLE,  # This sets the default to 'student'
        required=False  # Make this field optional
    )

    experience = serializers.CharField(required=False, allow_blank=True)  # New field
    bio = serializers.CharField(required=False, allow_blank=True)  # New field


    class Meta:
        model = User
        fields = ('first_name','email','phone_number','password', 'confirm_password','role','experience','bio')


    def validate(self,data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Password do not match')
        return data
    
    def create(self,validated_data):
        validated_data.pop('confirm_password')  # Remove confirm_password before creating the user

        user = User.objects.create_user(**validated_data)
        return user



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    #    Custom token serializer to include additional user information in the token.

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



from .models import CustomUser
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = fields = ['id', 'email', 'first_name', 'last_name', 'phone_number']
            