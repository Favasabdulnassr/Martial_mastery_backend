from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from  rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny,IsAuthenticated
from .serializers import RegisterSerializer,ProfileUpdateSerializer
from django.contrib.auth import get_user_model
from .serializers import MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
# from rest_framework_simplejwt.tokens import RefreshToken,AccessToken

User = get_user_model()

# Create your views here.




class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = RegisterSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User successfully registered'},status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



class MyTokenObtainPairView(TokenObtainPairView):
    # Custom view to use the custom token serializer
    
    serializer_class = MyTokenObtainPairSerializer




class ProfileUpdateView(APIView):
    permission_classes=[IsAuthenticated]

    def put(self,request):
        serializer = ProfileUpdateSerializer(request.user,data = request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
