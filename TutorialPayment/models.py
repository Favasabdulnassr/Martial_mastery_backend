from django.db import models
from django.conf import settings
from decimal import Decimal
from user_auth.models import CustomUser
from Tutorials.models import Tutorial
# Create your models here.

class TutorWallet(models.Model):
    tutor = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"walletf for {self.tutor.email}"


class Payment(models.Model):
    COMPLETED = 'completed'
    FAILED = 'failed'

    STATUS_CHOICES = [
        (COMPLETED,'Completed'),
        (FAILED,'Failed'),
    ]

    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='payments')
    tutorial = models.ForeignKey(Tutorial,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    stripe_payment_intent_id = models.CharField(max_length= 255,unique=True, null=True, blank=True)
    status = models.CharField(max_length=10,choices=STATUS_CHOICES,default=FAILED)
    created_at = models.DateTimeField(auto_now_add=True)    

    def __str__(self):
        return f"payment {self.stripe_payment_intent_id}"
    

class TutorialAccess(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    tutorial = models.ForeignKey(Tutorial,on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('user','tutorial')
        
    

