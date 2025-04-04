from rest_framework.response import Response
from django.db import transaction
from account.models import Account
from .models import Transaction
import logging


logger = logging.getLogger(__name__)

@transaction.atomic
def handle_charge_success(event_data):
    """
    Handles the charge success paystack webhook event by storing successful transactions
    in the database and empties the user's cart
    """
    customer_email = event_data['customer']['email']
    try:
        user = Account.objects.get(email=customer_email)
        
        # empty the user's cart since they have checked out the items
        cart = user.cart
        cart.products.clear()
        cart.save()
    except Account.DoesNotExist:
        return Response(status=404)

    try:
        transaction = Transaction.objects.get(reference=event_data['reference'])
        transaction.status = 'successful'
        transaction.save()
    except Account.DoesNotExist:
        return Response(status=404)

    logger.debug(f"Transaction with id {transaction.id} was successful")
    return Response(status=200)
