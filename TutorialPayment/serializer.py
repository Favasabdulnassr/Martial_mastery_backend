from rest_framework import serializers
from .models import Payment,TutorWallet

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'status', 'created_at']

        

class TutorWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorWallet
        fields = ['balance', 'created_at', 'updated_at']
