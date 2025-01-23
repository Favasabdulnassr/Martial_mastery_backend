import stripe
from rest_framework import status,viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import Payment
from Courses.models import Course
from .models import PurchasedCourse
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .serializers import PaymentSerializer
from rest_framework.decorators import action


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
            if PurchasedCourse.objects.filter(user=request.user, course=course).exists():
                return Response(
                    {"error": "Course already purchased"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create payment record
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
    print("=============== WEBHOOK RECEIVED ===============")
    print(f"Request Method: {request.method}")
    print(f"Headers: {request.headers}")
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    print(f"Signature Header: {sig_header}")


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
            print(f"Processing checkout session: {session.id}")
            
            # Get the payment   
            payment = Payment.objects.get(id=payment_id)
            
            # Update payment status
            payment.stripe_payment_intent_id = session['payment_intent']
            payment.payment_status = 'successful'
            payment.save()

            # Create PurchasedCourse
            purchased_course = PurchasedCourse.objects.create(
                user=payment.user,
                course=payment.course,
                tutor=payment.course.tutor,
                course_title=payment.course.title,
                course_description=payment.course.description,
                course_fees=payment.amount_paid,
                is_active=True
            )

            # Create purchased lessons
            purchased_course.create_purchased_lessons()

            print(f"Successfully processed payment and created course purchase for payment_id: {payment_id}")
            
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
from rest_framework.exceptions import PermissionDenied

class PurchasedCourseLessonListView(generics.ListAPIView):
    serializer_class = PurchasedCourseLessonSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access lessons

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        purchased_lessons = PurchasedCourseLesson.objects.filter(purchased_course_id=course_id)
        return purchased_lessons



class PurchasedCourseLessonDetailView(generics.RetrieveAPIView):
    serializer_class = PurchasedCourseLessonSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        course_id = self.kwargs['course_id']
        lesson_id = self.kwargs['lesson_id']


        lesson = get_object_or_404(
            PurchasedCourseLesson,
            id = lesson_id,
            purchased_course_id = course_id,
            purchased_course__user = self.request.user   
        ) 

        if not lesson.purchased_course.is_active:
            raise PermissionDenied("This course is no longer active")
        

        return lesson