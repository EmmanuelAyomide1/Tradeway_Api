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



def standardized_error_response(error_name, details, status_code):
    return {
        "status": status_code,
        "error": error_name,
        "details": details if isinstance(details, list) else [details]
    }

def custom_error_response(exc, context):
    #This will Try the default handler first
    response = exception_handler(exc, context)
    
    # if the default handler doesnt meet up to standard this Handle exceptions based on their types
    if response is None:
        if isinstance(exc, IntegrityError):
            details = [{"database_error": str(exc)}]
            return Response(
                standardized_error_response("IntegrityError", details, status.HTTP_400_BAD_REQUEST),
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, ValidationError):
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
            # This will handle all other Generic errors if the errors escape the elseif statement
            details = [{"server_error": "An unexpected error occurred"}]
            return Response(
                standardized_error_response("ServerError", details, status.HTTP_500_INTERNAL_SERVER_ERROR),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        # Handle DRF's standard exceptions
        data = response.data
        status_code = response.status_code
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
        
       
        response.data = standardized_error_response(error_name, details, status_code)
        return response