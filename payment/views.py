from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .webhook_handlers import handle_charge_success
from product.models import Order
from .models import Transaction
from .constants import PAYSTACK_BASE_URL
from .utils import get_paystack_headers
from .serializers import CheckoutSerializer
import logging, json, hmac, hashlib, requests, string, random


logger = logging.getLogger(__name__)

class CheckoutView(APIView):
    """
    Checks out all the items in a user's cart and initializes a payment.
    There must be items in the cart before a checkout can be initialized.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutSerializer

    @swagger_auto_schema(
        request_body=CheckoutSerializer,
        operation_summary='Check out items in a users cart'
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = serializer.validated_data['address']
        cart = request.user.cart

        # If the cart has not been created for the user, throw an error
        if cart == None:
            raise ValidationError('Account has no cart associated with it')

        # A payment cannot be initialized on an empty cart
        cart_products = cart.products.all()
        if len(cart_products) == 0:
            raise ValidationError('Cart does not have any items in it')

        # sum up items in the cart
        total_checkout_amount = sum([product.current_price for product in cart_products])

        try:  
            # Create an order containing all the products in the cart and initialize a pending transaction
            order = Order.objects.create(
                buyer=request.user,
                address=address,
                total_amount=total_checkout_amount
            )
            order.products.add(*cart_products)
            order.save()

            kobo_convertion = float(total_checkout_amount * 100)
            reference = 'TRDW-' + ''.join(random.choices(string.ascii_letters + string.digits, k=10))

            # Create pending transaction
            Transaction.objects.create(
                order=order,
                reference=reference
            )

            headers = get_paystack_headers()

            payload = {
                "email": request.user.email,
                "amount": kobo_convertion,
                "reference": reference
            }

            response = requests.post(f'{PAYSTACK_BASE_URL}/transaction/initialize', headers=headers, json=payload)
            response.raise_for_status()

            response_data = response.json()
            payment_link = response_data['data']['authorization_url']

            return Response({
                'message': 'Please follow the link finish your payment',
                'payment_link': payment_link
            })

        except requests.exceptions.RequestException as e:
            logger.error(str(e))
            error_message = response.json().get('message', 'An error occurred when initializing your payment')
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e))
            return Response({'message': 'Something went wrong when initializing your payment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyTransactionView(APIView):
    """
    Verifies a transaction after a successful payment.
    Transaction Status can be abandoned, failed, ongoing, pending, processing, queued, reversed or success.
    This endpoint would return a 200 status for all transaction status to show the transaction has been verified.
    Use the transaction_status field to know the actual status of the transasction.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Verify the payment status on a transaction"
    )
    def get(self, request, reference):
        try:
            headers = get_paystack_headers()
            endpoint = f'{PAYSTACK_BASE_URL}/transaction/verify/{reference}'
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()

            transaction_data = response.json()
            transaction_status = transaction_data['data']['status']

            return Response({'transaction_status': transaction_status}, status=status.HTTP_200_OK)

        except requests.exceptions.HTTPError as e:
            error_message = response.json().get('message', 'An error occurred when verifying the transaction')
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'Something went wrong when verifying the transaction'}, status=status.HTTP_500_INTERNAL_SERVER_ERRORS)


class WebhookHandlerView(APIView):
    """
    Handles Paystack events.
    Don't consume this endpoint
    """
    authentication_classes = []
    permission_classes = []

    @csrf_exempt
    @swagger_auto_schema(
        operation_summary="Webhook handler for paystack payments. Don't consume"
    )
    def post(self, request, *args, **kwargs):
        paystack_secret = settings.PAYSTACK_SECRET_KEY
        
        try:
            if 'x-paystack-signature' not in request.headers:
                logger.warning("Missing Paystack signature header")
                return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

            payload = request.body
            signature_header = request.headers['x-paystack-signature']

            if not payload:
                logger.warning("Empty payload received")
                return Response({"error": "Empty payload"}, status=status.HTTP_400_BAD_REQUEST)

            computed_hash = hmac.new(
                paystack_secret.encode('utf-8'), 
                payload, 
                digestmod=hashlib.sha512
            ).hexdigest()

            # Signature verification
            if computed_hash != signature_header:
                logger.warning("Signature verification failed")
                return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

            # Parse payload
            try:
                body = json.loads(payload.decode('utf-8'))
            except json.JSONDecodeError:
                logger.error("Failed to decode JSON payload")
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)

            # Validate event structure
            if 'event' not in body or 'data' not in body:
                logger.warning("Invalid event structure")
                return Response({"error": "Invalid event structure"}, status=status.HTTP_400_BAD_REQUEST)

            event = body['event']
            event_data = body['data']

            if event == 'charge.success':
                return handle_charge_success(event_data)

            # Unknown event type
            logger.debug(f"Unhandled event type: {event}")
            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
            return Response(
                {"error": "Internal server error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )