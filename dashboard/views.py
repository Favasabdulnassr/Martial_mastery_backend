from rest_framework import status,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from user_auth.models import CustomUser
from Courses.models import Course
from payment.models import Payment
from user_auth.permission import IsAdmin
from .serializer import PaymentSerializer
from payment.models import PurchasedCourseUser

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAdmin]

    @action(detail=False,methods=['get'])
    def get_stats(self,request):
        total_users = CustomUser.objects.exclude(role='admin').count()

        total_courses = Course.objects.count()

        total_revenue = Payment.objects.filter(
            payment_status='successful'
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0


        recent_payments = PaymentSerializer(
        Payment.objects.filter(payment_status='successful').order_by('-payment_date')[:5],
                               many=True
                                ).data
        
        students = PurchasedCourseUser.objects.values('user').distinct().count()
        
        response_data = ({
            'total_users':total_users,
            'total_courses':total_courses,
            'total_revenue':total_revenue,
            'recent_transactions':recent_payments,
            'user_roles':{
                'students':students,
                'tutors':CustomUser.objects.filter(role='tutor').count()
            },
            'course_status':{
                'pending':Course.objects.filter(status='pending').count(),
                'approved':Course.objects.filter(status='approved').count(),
                'rejected':Course.objects.filter(status='rejected').count()
            }

        })

        return Response(response_data)


    