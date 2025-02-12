from rest_framework import status,generics
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.shortcuts import get_object_or_404
from .serializers import CourseReportSerializer
from payment.models import PurchasedCourse
from user_auth.models import CustomUser
from .models import CourseReport
from user_auth.permission import IsAdmin
from payment.models import PurchasedCourse
from rest_framework.views import APIView
from .serializers import WalletSerializer
from .models import Wallet
from django.conf import settings
from django.core.mail import send_mail
from payment.models import PurchasedCourse

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_course(request):
    serializer =CourseReportSerializer(data=request.data)
    if serializer.is_valid():
        course =  get_object_or_404(PurchasedCourse,id=request.data.get('course'))
        print(course)
        tutor = get_object_or_404(CustomUser,id=request.data.get('tutorId'))
        print(tutor)

        if CourseReport.objects.filter(user=request.user,course=course).exists():
            return Response(
                {'detail':'YOu have already reported this course'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        report = serializer.save(
            user=request.user,
            course = course,
            tutor = tutor,

        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ReportedCoursesListView(generics.ListAPIView):
    permission_classes = [IsAdmin,IsAuthenticated]

    def list(self,request):
        report_courses = PurchasedCourse.objects.annotate(
            report_count=Count('report')
            ).filter(report_count__gt=0).values(
                'id',
                'course_title',
                'tutor__first_name',
                'report_count',
                'course__completed',
                'course__status',
                'course__id'

            )
        
        courses_data = [{
            'id':course['id'],
            'name':course['course_title'],
            'tutor_name':course['tutor__first_name'],
            'report_count':course['report_count'],
            'completed':course['course__completed'],
            'status':course['course__status'],
            'course_id':course['course__id']

        } for course in report_courses]

        return Response(courses_data)
    




class CourseReportDetailsView(generics.ListAPIView):
    permission_classes=[IsAdmin,IsAuthenticated]

    def list(self,request,course_id):
        reports =  CourseReport.objects.filter(
            course_id =course_id
        ).select_related('user').values(
            'id',
            'user__first_name',
            'reason',
            'details',
           
        )


        report_details = [{
            'id':report['id'],
            'student':report['user__first_name'],
            'reason':report['reason'],
            'detail':report['details'],
        }for report in reports]

        return Response(report_details)
    




class SendReportEmailsView(generics.CreateAPIView):
    """
    View to send emails to users about course reports
    """
    permission_classes = [IsAdmin,IsAuthenticated]
    
    def create(self, request):
        course_id  = request.data.get('courseIds')
        print('ppppppppppppppppppppppppppppppppppppppppppppppppp',course_id)
        email_content = request.data.get('emailContent', '')
        
        if not course_id:
            return Response({'error': 'courseIds is required'}, status=status.HTTP_400_BAD_REQUEST)

        course = PurchasedCourse.objects.get(id=course_id )
        print('mmmmmmmmmmmmmmmmm',course)
        tutor = course.tutor
        print('lllllllllllllllllllllllllll',tutor.email)    
        try:
            send_mail(
                'Course Report Notification',
                email_content,
                settings.EMAIL_HOST_USER,
                [tutor.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send email to {tutor.email}: {str(e)}")
        

        return Response({
            'message': f'Emails sent successfully to  recipients',
        }, status=status.HTTP_200_OK)

    


class TutorWalletView(APIView):
    def get(self,request,tutor_id):
        wallets = Wallet.objects.filter(user_id=tutor_id).order_by('-date')  

        # Calculate the current balance
        balance = wallets.first().balance if wallets.exists() else 0
        serializer = WalletSerializer(wallets, many=True)
        return Response({
            'balance': balance,
            'transactions': serializer.data
        }, status=status.HTTP_200_OK)
    



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Courses.models import Course

class UnlistCourseView(APIView):
    def post(self, request, course_id):
        try:
            print('aaaaaaaaaa')
            course = Course.objects.get(id=course_id)
            print('ssssssssssss',course)
            course.completed = False
            course.status = 'rejected'
            course.save()
            return Response({'message': 'Course unlisted successfully'}, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

