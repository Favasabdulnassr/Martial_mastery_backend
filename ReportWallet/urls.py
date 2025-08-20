from django.urls import path
from .views import report_course,ReportedCoursesListView,CourseReportDetailsView
from .views import TutorWalletView,SendReportEmailsView,UnlistCourseView,TutorWithdrawalView

urlpatterns = [
    path('reports/',report_course,name='reports'),
    path('admins/reports/',ReportedCoursesListView.as_view(),name='admin-reports'),
    path('reports/<int:course_id>/', CourseReportDetailsView.as_view(), name='report-detail'),
    path('reports/notify/', SendReportEmailsView.as_view(), name='report-notify'),
    path('courses/<int:course_id>/unlist/', UnlistCourseView.as_view(), name='course-unlist'),

    path('tutors/<int:tutor_id>/wallet/', TutorWalletView.as_view(), name='tutor-wallet'),  
    path('tutors/withdrawals/',TutorWithdrawalView.as_view(),name='tutor-withdrawals')

]
