from django.urls import path
from . import views 
from .views import StripeCheckoutView,PaymentViewSet,get_tutor_wallet

check_access = PaymentViewSet.as_view({'get':'check_access'})
successPayment = PaymentViewSet.as_view({'post':'payment_success'})

urlpatterns = [
    path('create-payment-session/',StripeCheckoutView.as_view(),name='payment-session'),
    path('check_access/',check_access,name='check_access'),
    path('paymentSuccess/',successPayment,name='paymentSuccess'),
    path('tutor-wallet/<int:tutor_id>/', views.get_tutor_wallet, name='tutor-wallet'),

]