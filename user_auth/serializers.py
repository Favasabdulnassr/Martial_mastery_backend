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
    print(email)

    phone_number = serializers.CharField(
        required = True,
        validators = [UniqueValidator(queryset=User.objects.all())]
    )
    print(phone_number)

    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)  # Add confirm_password field


    class Meta:
        model = User
        fields = ('first_name','email','phone_number','password', 'confirm_password')


    def validate(self,data):
        print(data,'data')
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
        token['is_superuser'] = user.is_superuser
        token['is_tutor'] = user.is_tutor
        token['phone_number'] = user.phone_number

        return token
        
        



class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name','last_name')