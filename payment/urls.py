from django.urls import path
from .views import PaymentGatewaySimulator, FieldStudentPaymentSimulator


urlpatterns = [
    path('simulator/', PaymentGatewaySimulator.as_view(), name='payment_simulator'),
    path('simulator/create_code/', FieldStudentPaymentSimulator.as_view(), name='create_code')
]
