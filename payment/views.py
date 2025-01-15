import stripe
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Payment
from Courses.models import Course
from .models import PurchasedCourse
from rest_framework.permissions import IsAuthenticated
stripe.api_key = settings.STRIPE_SECRET_KEY  # Add your Stripe secret key to settings.py

class InitiatePaymentAPIView(APIView):
    def post(self, request, course_id):
        try:
            # Get the course with proper error handling
            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                return Response(
                    {"message": "Course not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if the course has a tutor assigned
            if not course.tutor:
                return Response(
                    {"message": "Course does not have a tutor assigned"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if user has already purchased the course
            if not course.fees or float(course.fees) <= 0:
                return Response(
                    {"message": "Invalid course fees"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if PurchasedCourse.objects.filter(user=request.user, course=course).exists():
                return Response(
                    {"message": "You have already purchased this course"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create a Payment record
            try:
                payment = Payment.objects.create(
                    user=request.user,
                    course=course,
                    amount_paid=course.fees,
                    payment_status='pending'
                )
            except Exception as e:
                return Response(
                    {"message": f"Error creating payment: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Get the payment URL (Stripe Checkout)
            checkout_url = payment.get_payment_url()

            if isinstance(checkout_url, str) and checkout_url.startswith('http'):
                # Before redirecting, create a PurchasedCourse entry and associated lessons.
                purchased_course = PurchasedCourse.objects.create(
                    user=request.user,
                    course=course,
                    tutor=course.tutor,  # Set the tutor field to the course's tutor
                    course_title=course.title,
                    course_description=course.description,
                    course_fees=course.fees,
                    is_active=True
                )

                purchased_course.create_purchased_lessons()

                # Mark the payment as successful after creation.
                payment.mark_payment_successful()

                return Response({
                    "checkout_url": checkout_url,
                    "payment_id": payment.id,
                    "purchased_course_id": purchased_course.id
                })
            else:
                payment.delete()  # Delete the payment record if there was an error
                return Response(
                    {"message": f"Unable to create payment session: {checkout_url}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



from .serializers import PurchasedCourseSerializer
class PurchasedCoursesView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    
    def get(self, request):
        # Filter purchased courses for the authenticated user
        purchased_courses = PurchasedCourse.objects.filter(user=request.user)
        
        # Serialize the data
        serializer = PurchasedCourseSerializer(purchased_courses, many=True)
        
        return Response(serializer.data)
    
from rest_framework import generics
from .serializers import PurchasedCourseLessonSerializer
from .models import PurchasedCourseLesson

class PurchasedCourseLessonListView(generics.ListAPIView):
    serializer_class = PurchasedCourseLessonSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access lessons

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        purchased_lessons = PurchasedCourseLesson.objects.filter(purchased_course_id=course_id)
        return purchased_lessons
