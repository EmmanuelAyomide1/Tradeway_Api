import os
import sys
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        custom_response = {"error": exc.__class__.__name__, "message": str(exc)}
        return Response(custom_response, status=status.HTTP_400_BAD_REQUEST)
    return response
