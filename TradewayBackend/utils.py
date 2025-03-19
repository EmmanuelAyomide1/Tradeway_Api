import os
import sys
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import Http404

from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError



def standardized_error_response(error_name, details, status_code):
    return {
        "status": status_code,
        "error": error_name,
        "details": details if isinstance(details, list) else [details]
    }


def custom_exception_handler(exc, context):

    if isinstance(exc, DRFValidationError):
        error_name = "ValidationError"
        status_code = status.HTTP_400_BAD_REQUEST
        details = []
        
        if isinstance(exc.detail, dict):
            field_errors = {}
            for field, errors in exc.detail.items():
                if isinstance(errors, list):
                    field_errors[field] = " ".join(str(e) for e in errors)
                else:
                    field_errors[field] = str(errors)
            details = [field_errors]
        elif isinstance(exc.detail, list):
            field_errors = {"error": " ".join(str(e) for e in exc.detail)}
            details = [field_errors]
        else:
            field_errors = {"error": str(exc.detail)}
            details = [field_errors]
            
        return Response(
            standardized_error_response(error_name, details, status_code),
            status=status_code
        )
    
    # Try the default handler for other exceptions
    response = exception_handler(exc, context)
    
    if response is None:
        # Handle exceptions not caught by DRF's exception handler
        if isinstance(exc, IntegrityError):
            details = [{"database_error": str(exc)}]
            return Response(
                standardized_error_response("IntegrityError", details, status.HTTP_400_BAD_REQUEST),
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, DjangoValidationError):
            if hasattr(exc, 'message_dict'):
                details = [{field: msgs} for field, msgs in exc.message_dict.items()]
            else:
                details = [{"validation_error": str(exc)}]
            return Response(
                standardized_error_response("ValidationError", details, status.HTTP_400_BAD_REQUEST),
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, PermissionDenied):
            details = [{"permission": "You do not have permission to perform this action"}]
            return Response(
                standardized_error_response("PermissionDenied", details, status.HTTP_403_FORBIDDEN),
                status=status.HTTP_403_FORBIDDEN
            )
        elif isinstance(exc, Http404):
            details = [{"not_found": "Resource not found"}]
            return Response(
                standardized_error_response("NotFound", details, status.HTTP_404_NOT_FOUND),
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            # Get the actual error name for other exceptions
            error_name = exc.__class__.__name__
            details = [{"error": str(exc)}]
            return Response(
                standardized_error_response(error_name, details, status.HTTP_500_INTERNAL_SERVER_ERROR),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        # Handle DRF's standard exceptions
        data = response.data
        status_code = response.status_code
        
        # Get a more specific error name based on the exception type
        view = context.get('view', None)
        if view:
            exception_class = getattr(exc, '__class__', None)
            if exception_class:
                error_name = exception_class.__name__
            else:
                error_name = "APIError"
        else:
            error_name = "APIError"
        
        details = []
        
        if isinstance(data, dict):
            if "detail" in data:
                error_message = str(data["detail"])
                if status_code == 400:
                    error_name = "BadRequest"
                elif status_code == 401:
                    error_name = "Unauthorized"
                elif status_code == 403:
                    error_name = "Forbidden"
                elif status_code == 404:
                    error_name = "NotFound"
                elif status_code == 405:
                    error_name = "MethodNotAllowed"
                details = [{"error": error_message}]
            else:
                # Handle validation errors with multiple fields
                error_name = "ValidationError"
                field_errors = {}
                for field, errors in data.items():
                    if isinstance(errors, list):
                        field_errors[field] = " ".join(str(e) for e in errors)
                    else:
                        field_errors[field] = str(errors)
                details = [field_errors]
        elif isinstance(data, list):
            details = [{"error": str(item)} for item in data]
        else:
            details = [{"error": str(data)}]
        
        # Update the response data with our standardized format
        response.data = standardized_error_response(error_name, details, status_code)
        return response