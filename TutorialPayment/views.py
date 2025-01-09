import stripe
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from Tutorials.models import Tutorial
from .models import Payment,TutorialAccess,TutorWallet
from rest_framework.views import APIView
from django.db import transaction
from decimal import Decimal
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from datetime import datetime





stripe.api_key = settings.STRIPE_SECRET_KEY


from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeCheckoutView(APIView):
    def post(self, request):
        tutorial_id = request.data.get('tutorial_id')
        try:
            # Get the tutorial
            tutorial = Tutorial.objects.get(id=tutorial_id)

            payment_intent = stripe.PaymentIntent.create(
                amount=1,
                currency='usd',
                metadata={
                    'tutorial_id':'tutorial_id',
                    'user_id':request.user.id,
                }
            )

            # Create a Stripe Checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': tutorial.title,
                            },
                            'unit_amount': 1,  # $12 in cents
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=f"{settings.SITE_URL}/courses?success=true&tutorial_id={tutorial_id}&payment_intent_id={payment_intent.id}",
                cancel_url=f"{settings.SITE_URL}/courses?cancelled=true",
                metadata={
                    'tutorial_id':tutorial_id,
                    'user_id':request.user.id
                }
            )

            return Response({'url': checkout_session.url,
                             'payment_intent_id': payment_intent.id
                             })

        except Tutorial.DoesNotExist:
            return Response({'error': 'Tutorial not found'}, status=404)
        except Exception as e:
            print(f"errorrrrrrrrrrrrrrrrrrrrrrrrrr{e}")
            return Response({'error': str(e)}, status=500)


    


class PaymentViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def check_access(self, request):
        tutorial_id = request.query_params.get('tutorial_id')
        has_access = TutorialAccess.objects.filter(
            user=request.user,
            tutorial_id=tutorial_id
        ).exists()
        
        return Response({
            'has_access': has_access
        })
    

    @action(detail=False, methods=['post'])
    def payment_success(self, request):
        payment_intent_id = request.data.get('payment_intent_id')
        print('aaaaaaaaaaaaaaaa', payment_intent_id)
        tutorial_id = request.data.get('tutorial_id')
        print('bbbbbbbbbbbbbbbbbbbbb', tutorial_id)

        # Validate if payment_intent_id and tutorial_id exist
        if not payment_intent_id or not tutorial_id:
            return Response(
                {'error': 'Payment Intent ID or Tutorial ID is missing'},
                status=status.HTTP_400_BAD_REQUEST
            )

       
        # Perform database operations inside an atomic block
        with transaction.atomic():
            # Check if tutorial exists
            tutorial = Tutorial.objects.filter(id=tutorial_id).first()
            if not tutorial:
                return Response(
                    {'error': 'Tutorial not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            

      
            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                tutorial_id=tutorial_id,
                amount=Decimal('1.00'),  # Fixed amount
                stripe_payment_intent_id=payment_intent_id,
                status=Payment.COMPLETED
            )

            

            # Create tutorial access
            TutorialAccess.objects.create(
                user=request.user,
                tutorial_id=tutorial_id,
                payment=payment
            )
            

            # Update tutor's wallet (80% of payment)
            tutor_amount = Decimal('1.00') * Decimal('0.8')  # 80% of the amount
            wallet, _ = TutorWallet.objects.get_or_create(tutor=tutorial.tutor)
            wallet.balance = Decimal(str(wallet.balance)) if isinstance(wallet.balance, float) else wallet.balance
            

            wallet.balance += tutor_amount
            wallet.save()

        return Response({
            'status': 'success',
            'message': 'Payment processed successfully'
        })





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tutor_wallet(request, tutor_id):
    wallet = get_object_or_404(TutorWallet, tutor_id=tutor_id)
    payments = Payment.objects.filter(user_id=tutor_id).order_by('-created_at')
    
    transactions = []
    for payment in payments:
        transactions.append({
            'type': 'credit' if payment.status == Payment.COMPLETED else 'debit',
            'amount': float(payment.amount),
            'description': f"Payment for {payment.tutorial.title}" if payment.tutorial else "Withdrawal",
            'created_at': payment.created_at
        })
    
    return Response({
        'balance': float(wallet.balance),
        'transactions': transactions
    })
















