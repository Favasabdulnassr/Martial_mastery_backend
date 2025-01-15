from rest_framework import serializers
from .models import PurchasedCourse

class PaymentSerializer(serializers.ModelSerializer):
    tutor = serializers.SerializerMethodField()
    class Meta:
        model = PurchasedCourse
        fields = ['id', 'user', 'course', 'tutor','amount_paid', 'payment_status', 'payment_date', 'stripe_session_id', 'stripe_payment_intent_id']

    def create(self, validated_data):
        # You can add additional logic for creating a Payment instance if necessary.
        return super().create(validated_data)




from rest_framework import serializers
from .models import PurchasedCourse
from user_auth.serializers import CustomUserSerializer  # Import CustomUser serializer

class PurchasedCourseSerializer(serializers.ModelSerializer):
    tutor = CustomUserSerializer(read_only=True)  # Nested serializer for tutor
    course_title = serializers.CharField(source='course.title')
    course_description = serializers.CharField(source='course.description')
    course_fees = serializers.DecimalField(source='course.fees', max_digits=10, decimal_places=2)

    class Meta:
        model = PurchasedCourse
        fields = ['id', 'user', 'tutor', 'course', 'course_title', 'course_description', 'course_fees', 'purchase_date', 'is_active']



# payment/serializers.py

from rest_framework import serializers
from .models import PurchasedCourseLesson
from cloudinary.models import CloudinaryField

class PurchasedCourseLessonSerializer(serializers.ModelSerializer):
    cloudinary_url = CloudinaryField()  # CloudinaryField will handle the URL for the video
    
    class Meta:
        model = PurchasedCourseLesson
        fields = ['id', 'title', 'description', 'cloudinary_url', 'thumbnail', 'order', 'created_at', 'updated_at']
