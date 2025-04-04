from typing import Dict
from django.conf import settings

def get_paystack_headers() -> Dict:
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
