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
import random
from twilio.rest import Client
from django.conf import settings
import phonenumbers
from datetime import datetime, timedelta
from django.contrib.sessions.models import Session
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination




# from rest_framework_simplejwt.tokens import RefreshToken,AccessToken

User = get_user_model()

# Create your views here.




class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = RegisterSerializer(data = request.data)
        if serializer.is_valid():
            role = serializer.validated_data['role']
            recipient_mail = serializer.validated_data['email']

            request.session['registration_data'] = serializer.validated_data


            otp = str(random.randint(100000,999999))
            request.session['otp'] = otp

            expiration_time = datetime.now() + timedelta(minutes=2)
            request.session['otp_expiration'] = expiration_time.isoformat()

            
            request.session.save()


            
            if role == 'student':
                phone_number = serializer.validated_data['phone_number']
                try:
                    # Parse phone number with default region

                    parsed_number = phonenumbers.parse(phone_number, "IN")    # Replace "IN" with your default country code (e.g., "US" for the USA)

                    # Check if the number is valid
                    if not phonenumbers.is_valid_number(parsed_number):
                        return Response({'message': 'Invalid phone number'}, status=status.HTTP_400_BAD_REQUEST)

                    # Format the number to E.164 format
                    formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)

                    # Send OTP via Twilio
                    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    client.messages.create(
                        to=formatted_number,  # Use formatted number
                        from_=settings.TWILIO_NUMBER,
                        body=f"Your OTP is {otp}"
                    )

                    return Response(
                        {'message': 'OTP sent successfully. Verify to complete registration',
                        'otp_expiration': expiration_time.isoformat(),
                        'session_id': request.session.session_key,  # Send the session ID (cookie)

                        
                        },
                        status=status.HTTP_201_CREATED
                    )

                except phonenumbers.phonenumberutil.NumberParseException:
                    return Response({'message': 'Invalid phone number format'}, status=status.HTTP_400_BAD_REQUEST)

            elif role == 'tutor':
                subject = 'your 6 digit OTP for email verification'
                message = f"Your email verification is {otp}"
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [recipient_mail]
                send_mail(subject,message,from_email,recipient_list,fail_silently=False)

                return Response(
                        {'message': 'OTP sent successfully. Verify to complete registration',
                        'otp_expiration': expiration_time.isoformat(),
                        'session_id': request.session.session_key,  # Send the session ID (cookie)

                        
                        },
                        status=status.HTTP_201_CREATED
                    )

            
        print("Serializer errors",serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class VerifyOtpView(APIView):
    permission_classes = [AllowAny]
    

    def post(self, request):

        otp = request.data.get('otp')
        session_otp = request.session.get('otp')
        session_id = request.data.get('sessionId')

        try:
            session = Session.objects.get(session_key=session_id)
            session_data = session.get_decoded()  # Decode the session data
        except Session.DoesNotExist:
            return Response({'error': 'Invalid session ID or session does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

         # Extract necessary data from the session

        session_otp = session_data.get('otp')
        registration_data = session_data.get('registration_data')
        otp_expiration = session_data.get('otp_expiration')


        # Check if session data exists
        if not session_otp or not registration_data or not otp_expiration:
            return Response(
                {'error': 'Session expired or no registration data found.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if OTP has expired
        current_time = datetime.now()
        expiration_time = datetime.fromisoformat(otp_expiration)  # Convert ISO format back to datetime
        if current_time > expiration_time:
            # Clear session data if expired
            session.delete()

            return Response(
                {'error': 'OTP has expired. Please register again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate OTP
        if otp == session_otp:
            # Create user and clear session
            registration_data.pop('confirm_password', None)
            User.objects.create_user(**registration_data)
            session.delete()
            return Response({'message': 'Registration completed successfully'}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)




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
    
class ProfilePictureView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes=[IsAuthenticated]

    def get(self,request):
        user = request.user
        if not user.profile:
            return Response({"detail":"No profile picture found"},status=status.HTTP_404_NOT_FOUND)

    def post(self,request):
        user = request.user
        print(user)
        print(request)
        profile_Picture =  request.FILES.get('profile')
        print(profile_Picture)

        if not profile_Picture:
            return Response({"detail":"No file provided"},status=status.HTTP_400_BAD_REQUEST)      
        
        user.profile = profile_Picture
        user.save()
        serializer = ProfileUpdateSerializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def delete(self,request):
        user =  request.user
        user.profile.delete()
        user.profile = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)



class UserListView(APIView):
    permission_classes = [IsAuthenticated]


    class StandardResultsSetPagination(PageNumberPagination):
        page_size = 5
    
    def get(self,request):
        search_query = request.query_params.get('search','')
        if search_query:
            users = User.objects.filter(
                Q(first_name__icontains = search_query)|
                Q(email__icontains=search_query),
                role='student'
            ).order_by('id')
        else:
            users = User.objects.filter(role='student').order_by('id')

        paginator = self.StandardResultsSetPagination()

        result_page = paginator.paginate_queryset(users,request)
        serializer = ProfileUpdateSerializer(result_page,many=True)
        return paginator.get_paginated_response(serializer.data)
    

class TutorListView(APIView):
    permission_classes = [IsAuthenticated]

    class StandardResultSetPagination(PageNumberPagination):
        page_size = 5

        

    def get(self,request):
        search_query = request.query_params.get('search','')
        
        if search_query:
            users = User.objects.filter(
                Q(first_name__icontains= search_query)|
                Q(email__icontains=search_query),
                role = 'tutor'
            ).order_by('id')
        else:
            users = User.objects.filter(role='tutor').order_by('id')


        paginator = self.StandardResultSetPagination()
        result_page = paginator.paginate_queryset(users,request)

        serializer = ProfileUpdateSerializer(result_page,many=True)
        return paginator.get_paginated_response(serializer.data)
               
    


    
class TutorRegister(APIView):
    permission_classes = [AllowAny]

    

    def post(self,request):
        print('ddddddddddddatat',request.data)
        serializer = RegisterSerializer(data=request.data)
        print('suuuuuuuuuuuuuuuuuuuui',serializer)
        print('vvvvvvvv')
        if serializer.is_valid():
            print('ccccccccccccc')
            serializer.save()

            return Response(
                {'message':'tutor created successfully'},
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    


class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')  # Get confirm password from request



        user = request.user
        
        if not user.check_password(current_password):
            return Response({'message':'current password is incorrect'},status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 6:
            return Response({'message':'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({'message': 'New password and confirm password do not match'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()

        return Response({'success': True, 'message': 'Password changed successfully'}, status=status.HTTP_200_OK)