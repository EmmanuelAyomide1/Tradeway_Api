from django.urls import path
from .views import WebhookHandlerView, CheckoutView, VerifyTransactionView


urlpatterns = [
  path('webhook', WebhookHandlerView.as_view(), name='webhook'),
  path('checkout', CheckoutView.as_view(), name='checkout'),
  path('<str:reference>/verify', VerifyTransactionView.as_view(), name='verify-transaction')
]