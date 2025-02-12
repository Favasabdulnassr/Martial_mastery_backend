from rest_framework import serializers
from .models import CourseReport,Wallet

class CourseReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseReport
        fields = ['id', 'course', 'reason', 'details', 'created_at']
        read_only_fields = ['user', 'tutor', 'is_reviewed']


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'date', 'transaction_type', 'transaction_details', 'amount', 'balance']