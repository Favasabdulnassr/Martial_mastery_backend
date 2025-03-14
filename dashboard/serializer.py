from rest_framework import serializers
from payment.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'amount_paid', 'payment_date', 'payment_status', 
                  'user_id', 'course_id', 'user_email', 'course_title']