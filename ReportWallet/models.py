from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from user_auth.models import CustomUser
from payment.models import PurchasedCourse


class CourseReport(models.Model):
    REPORT_REASONS = [
        ('inappropriate','Inappropriate Content'),
        ('misleading','Misleading Description'),
        ('quality','Poor Quality'),
        ('other','Other'),
    ]

    course = models.ForeignKey(PurchasedCourse,on_delete=models.CASCADE,related_name='report')
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='course_reports')
    tutor = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='course_tutor_reports')
    reason = models.CharField(max_length=20,choices=REPORT_REASONS)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)


    class Meta:
        unique_together = ('course','user')


   



class Wallet(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=50, null=True)
    transaction_details = models.CharField(max_length=50, null=True)
    amount = models.PositiveIntegerField(default=0)
    balance = models.PositiveBigIntegerField(default=0)

        