from django.contrib import admin
from .models import Payment,PurchasedCourse,PurchasedCourseLesson,PurchasedCourseUser

# Register your models here.

admin.site.register(Payment)
admin.site.register(PurchasedCourseLesson)
admin.site.register(PurchasedCourse)
admin.site.register(PurchasedCourseUser)