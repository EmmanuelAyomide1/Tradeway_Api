from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        custom_response = {"error": exc.__class__.__name__, "message": str(exc)}
        return Response(custom_response, status=status.HTTP_400_BAD_REQUEST)
    return response

def custom_error_response(message, code):
    if type(message) != str:
        error_data = []
        data_len = len(message.items())
        if data_len == 1:
            for field, value in message.items():
                error_data = "".join(value)
        if data_len > 1:
            error_data = []
            for field, value in message.items():
                error_data.append(" ".join(value))
        message = error_data
    return Response(
        {
            "error": True,
            "message": message,
        },
        status=code,
    )
