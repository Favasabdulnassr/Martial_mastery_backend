from rest_framework import serializers
from .models import PurchasedCourse,Payment,PurchasedCourseUser
from user_auth.models import CustomUser

# class PaymentSerializer(serializers.ModelSerializer):
#     tutor = serializers.SerializerMethodField()
#     class Meta:
#         model = PurchasedCourse
#         fields = ['id', 'user', 'course', 'tutor','amount_paid', 'payment_status', 'payment_date', 'stripe_session_id', 'stripe_payment_intent_id']

#     def create(self, validated_data):
#         # You can add additional logic for creating a Payment instance if necessary.
#         return super().create(validated_data)


# payment/serializers.py



class PaymentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user_email', 'course_title', 'amount_paid',
            'payment_status', 'payment_date', 'last_error'
        ]
        read_only_fields = ['payment_status', 'last_error']


from rest_framework import serializers
from .models import PurchasedCourse
from user_auth.serializers import CustomUserSerializer  # Import CustomUser serializer

class PurchasedCourseSerializer(serializers.ModelSerializer):
    tutor = CustomUserSerializer(read_only=True)
    course_title = serializers.CharField(source='course.title')
    course_description = serializers.CharField(source='course.description')
    course_fees = serializers.DecimalField(source='course.fees', max_digits=10, decimal_places=2)
    purchased_date = serializers.SerializerMethodField()
    

    class Meta:
        model = PurchasedCourse
        fields = [
            'id', 'tutor', 'course', 'course_title', 
            'course_description', 'course_fees', 
            'purchased_date', 'is_active'
        ]

    def get_purchased_date(self, obj):
        # Get the earliest purchase date for this course
        first_purchase = obj.purchased_users.order_by('purchased_at').first()
        return first_purchase.purchased_at if first_purchase else None



# payment/serializers.py

from rest_framework import serializers
from .models import PurchasedCourseLesson
from cloudinary.models import CloudinaryField

class PurchasedCourseLessonSerializer(serializers.ModelSerializer):
    cloudinary_url = CloudinaryField()  # CloudinaryField will handle the URL for the video
    
    class Meta:
        model = PurchasedCourseLesson
        fields = ['id', 'title','description', 'cloudinary_url', 'thumbnail', 'order', 'created_at', 'updated_at']





class PurchasedCourseSerializer(serializers.ModelSerializer):
    tutor_id = serializers.IntegerField(source='tutor.id',read_only=True)

    class Meta:
        model = PurchasedCourse
        fields = ['id','tutor_id', 'course_title', 'course_description', 'course_fees', 'purchase_date']

class StudentWithCoursesSerializer(serializers.ModelSerializer):
    purchased_courses = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser  # Replace with your actual user model
        fields = ['id', 'email', 'first_name', 'last_name','phone_number', 'purchased_courses']  # Include purchased courses

    def get_purchased_courses(self, obj):
        # Get the tutor ID from the context
        tutor_id = self.context.get('tutor_id')
        
        # Get all PurchasedCourse instances for the tutor
        purchased_courses = PurchasedCourse.objects.filter(tutor__id=tutor_id)
        
        # Get all PurchasedCourseUser instances for this student and the tutor's courses
        purchased_course_users = PurchasedCourseUser.objects.filter(
            user=obj,
            purchased_course__in=purchased_courses
        )
        
        # Serialize the purchased courses
        return PurchasedCourseSerializer(
            [pcu.purchased_course for pcu in purchased_course_users],
            many=True
        ).data