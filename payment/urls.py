from django.urls import path
from .views import PaymentGatewaySimulator, CreateCodePaymentSimulator, MoneyTransferSimulator


urlpatterns = [
    path('simulator/', PaymentGatewaySimulator.as_view(), name='payment_simulator'),
    path('simulator/create_code/', CreateCodePaymentSimulator.as_view(), name='create_code'),
    path('transfer/create_code/', CreateCodePaymentSimulator.as_view(), name='create_code2'),
    path('transfer/', MoneyTransferSimulator.as_view(), name='money_transfer')
]
