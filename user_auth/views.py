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


# from rest_framework_simplejwt.tokens import RefreshToken,AccessToken

User = get_user_model()

# Create your views here.




class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = RegisterSerializer(data = request.data)
        if serializer.is_valid():
            request.session['registration_data'] = serializer.validated_data


            otp = str(random.randint(100000,999999))
            request.session['otp'] = otp

            expiration_time = datetime.now() + timedelta(minutes=2)
            request.session['otp_expiration'] = expiration_time.isoformat()

            
            request.session.save()


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
    
