import stripe
from rest_framework import status,viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import Payment
from Courses.models import Course
from .models import PurchasedCourse,PurchasedCourseUser
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .serializers import PaymentSerializer
from rest_framework.decorators import action
from .serializers import PurchasedCourseSerializer
   
from rest_framework import generics
from .serializers import PurchasedCourseLessonSerializer,StudentWithCoursesSerializer
from .models import PurchasedCourseLesson
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import NotFound
from user_auth.permission import IsTutor
from rest_framework import generics
from ReportWallet.models import Wallet

# stripe listen --forward-to http://127.0.0.1:8000/payment/webhook/ --log-level debug

stripe.api_key = settings.STRIPE_SECRET_KEY
import logging

logger = logging.getLogger(__name__)

class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def initiate(self, request,pk=None):

        try:

            course = Course.objects.get(id=pk)



            # Validation checks
            if PurchasedCourseUser.objects.filter( user=request.user, purchased_course__course=course).exists():
                return Response(
                    {"error": "Course already purchased"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create payment record
            print('aaaaaaaaaaa')

            payment = Payment.objects.create(
                user=request.user,
                course=course,
                amount_paid=course.fees
            )


            # Get checkout URL
            checkout_url = payment.create_stripe_session()

            return Response({
                "checkout_url": checkout_url,
                "payment_id": payment.id
            })

        except Course.DoesNotExist:
            return Response(
                {"error": "Course not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Payment error: {str(e)}")
            return Response(
                {"error": "Failed to process payment"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# @csrf_exempt
# @require_POST
def stripe_webhook(request):
   
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')


    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_ENDPOINT_SECRET
        )
    except Exception as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        try:
            session = event['data']['object']
            payment_id = session['metadata']['payment_id']
            
            # Get the payment   
            payment = Payment.objects.get(id=payment_id)
            
            # Update payment status
            payment.stripe_payment_intent_id = session['payment_intent']
            payment.payment_status = 'successful'
            payment.save()


            tutor_share = int(float(payment.amount_paid) * 0.80)

            # Create wallet entry for tutor
            Wallet.objects.create(
                user=payment.course.tutor,
                transaction_type='course_sale',
                transaction_details=f"Course purchase: {payment.course.title}",
                amount=tutor_share,
                balance=Wallet.objects.filter(user=payment.course.tutor).last().balance + tutor_share if Wallet.objects.filter(user=payment.course.tutor).exists() else tutor_share
            )





                       # Check if PurchasedCourse already exists
            purchased_course, created = PurchasedCourse.objects.get_or_create(
                course=payment.course,
                defaults={
                    'course_title': payment.course.title,
                    'course_description': payment.course.description,
                    'course_fees': payment.amount_paid,
                    'tutor': payment.course.tutor,
                    'is_active': True
                }
            )

            # Create PurchasedCourseUser entry
            PurchasedCourseUser.objects.get_or_create(
                purchased_course=purchased_course,
                user=payment.user
            )

            # If this is a newly created purchased course, create purchased lessons
            if created:
                for lesson in purchased_course.course.tutorials.all():
                    PurchasedCourseLesson.objects.create(
                        purchased_course=purchased_course,
                        title=lesson.title,
                        description=lesson.description,
                        cloudinary_url=lesson.cloudinary_url,
                        thumbnail=lesson.thumbnail,
                        order=lesson.order
                    )

            print(f"Successfully processed payment and course purchase for payment_id: {payment_id}")
            return HttpResponse(status=200)
        except Payment.DoesNotExist:
            print(f"Payment not found for session {session['id']}")
            return HttpResponse(status=400)
        except Exception as e:
            print(f"Error processing webhook: {str(e)}")
            return HttpResponse(status=400)

    elif event['type'] == 'payment_intent.payment_failed':
        try:
            payment_intent = event['data']['object']
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
            payment.payment_status = 'failed'
            payment.last_error = payment_intent.get('last_payment_error', {}).get('message')
            payment.save()
        except Payment.DoesNotExist:
            print(f"Payment not found for payment_intent {payment_intent['id']}")

    return HttpResponse(status=200)



class PurchasedCoursesView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    
    def get(self, request):
        # Filter purchased courses for the authenticated user
        purchased_courses_users = PurchasedCourseUser.objects.filter(user=request.user)
        purchased_courses = [pcu.purchased_course for pcu in purchased_courses_users]
        
        # Serialize the data
        serializer = PurchasedCourseSerializer(purchased_courses, many=True)
        
        return Response(serializer.data)
 

class PurchasedCourseLessonListView(generics.ListAPIView):
    serializer_class = PurchasedCourseLessonSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access lessons

    def get_queryset(self):
        course_id = self.kwargs['course_id']
         # Check if user has purchased the course
        purchased_course_user = PurchasedCourseUser.objects.filter(
            user=self.request.user,
            purchased_course_id=course_id
        ).exists()
        
        if not purchased_course_user:
            raise PermissionDenied("You have not purchased this course")
        
        return PurchasedCourseLesson.objects.filter(purchased_course_id=course_id)





class TutorPurchasedCourseLessonListView(generics.ListAPIView):
    serializer_class = PurchasedCourseLessonSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access lessons

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        user = self.request.user

        # Check if the user is a tutor for the given course
        purchased_course = PurchasedCourse.objects.filter(
            tutor=user,
        )

        print('sssssssssss',purchased_course)

        # If the user is not the tutor for this course, raise permission denied
        if not purchased_course:
            raise PermissionDenied("You are not the tutor for this course")

        # Return the lessons associated with the purchased course
        return PurchasedCourseLesson.objects.filter(purchased_course_id=course_id).order_by('order')







class PurchasedCourseLessonDetailView(generics.RetrieveAPIView):
    serializer_class = PurchasedCourseLessonSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        course_id = self.kwargs['course_id']
        lesson_id = self.kwargs['lesson_id']

        purchased_course_user = get_object_or_404(
            PurchasedCourseUser,
            user=self.request.user,
            purchased_course_id=course_id
        )

        lesson = get_object_or_404(
            PurchasedCourseLesson,
            id=lesson_id,
            purchased_course_id=course_id
        )

        if not lesson.purchased_course.is_active:
            raise PermissionDenied("This course is no longer active")

        return lesson
    

class TutorPurchasedCourseLessonDetailView(generics.RetrieveAPIView):
    serializer_class = PurchasedCourseLessonSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        course_id = self.kwargs['course_id']
        lesson_id = self.kwargs['lesson_id']
        print(course_id)
        print(lesson_id)

       
        lesson = get_object_or_404(
            PurchasedCourseLesson,
            id = lesson_id,
            purchased_course_id = course_id
        )

        if not lesson.purchased_course.is_active:
            raise PermissionDenied("This course is no longer active")
        
        return lesson
        
    



class PurchasedCourseByTutorView(generics.ListAPIView):
    serializer_class = PurchasedCourseSerializer
    permission_classes = [IsAuthenticated,IsTutor] 

    def get_queryset(self):
      
        user = self.request.user
        purchased_courses = PurchasedCourse.objects.filter(tutor=user)
        
        if not purchased_courses.exists():
            raise NotFound("No purchased courses found for your account.")
        
        return purchased_courses





class TutorStudentsListView(generics.ListAPIView):
    serializer_class = StudentWithCoursesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the tutor ID from the URL parameters
        tutor_id = self.kwargs['tutor_id']
        
        # Get all PurchasedCourse instances for the tutor
        purchased_courses = PurchasedCourse.objects.filter(tutor__id=tutor_id)
        
        # Get all PurchasedCourseUser instances for these courses
        purchased_course_users = PurchasedCourseUser.objects.filter(purchased_course__in=purchased_courses)
        
        # Extract unique students from the PurchasedCourseUser instances
        students = set(pcu.user for pcu in purchased_course_users)
        
        return students

    def get_serializer_context(self):
        # Pass the tutor_id to the serializer context
        context = super().get_serializer_context()
        context['tutor_id'] = self.kwargs['tutor_id']
        return context