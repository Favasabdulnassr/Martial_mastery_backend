from django.urls import path
from .views import report_course,ReportedCoursesListView,CourseReportDetailsView
from .views import TutorWalletView,SendReportEmailsView,UnlistCourseView,TutorWithdrawalView

urlpatterns = [
    path('report/course',report_course,name='report_course'),
    path('adminside/reported-courses',ReportedCoursesListView.as_view(),name='reported_courses'),
    path('adminside/course-reports/<int:course_id>/', CourseReportDetailsView.as_view(), name='course-report-details'),
    path('send-report-emails/', SendReportEmailsView.as_view(), name='send-report-emails'),
     path('unlist-course/<int:course_id>/', UnlistCourseView.as_view(), name='unlist-course'),

    path('tutor-wallet/<int:tutor_id>/', TutorWalletView.as_view(), name='tutor-wallet'),  
    path('tutor-withdrawal/',TutorWithdrawalView.as_view(),name='withdrawal')

]
