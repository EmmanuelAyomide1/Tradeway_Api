from django.db import transaction
from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import views, status

from account.models import Account

from .emails import send_verification_email, send_password_reset_email
from .models import Otp
from .serializers import (
    SignUpSerializer,
    LoginUserSerializer,
    LogoutSerializer,
    OTPVerificationSerializer,
    ResendOTPSerializer,
    ResetPasswordSerializer,
    ForgottenPasswordSerializer,
    GoogleSocialAuthSerializer
)


class SignUpView(views.APIView):
    permission_classes = []
    serializer_class = SignUpSerializer

    @transaction.atomic
    @swagger_auto_schema(
        tags=["Authentication"],
        request_body=serializer_class,
        operation_summary="Register a user",
        operation_description="Registers a user on the platform and sends an OTP to the user's email for verification",
        responses={
            201: "Account created successfully, check your email for verification",
            400: "Bad Request",
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # send otp
        user = serializer.instance
        otp_obj = Otp.generate_otp(user=user)
        
        send_verification_email(
            name=user.name,
            email=user.email,
            otp=otp_obj.otp
        )

        return Response(
            {"message": "Account created successfully, check your email for verification"},
            status=status.HTTP_201_CREATED,
        )


class LoginView(views.APIView):
    permission_classes = []
    serializer_class = LoginUserSerializer

    @swagger_auto_schema(
        tags=["Authentication"],
        request_body=serializer_class,
        operation_summary="Log in a user",
        operation_description="Logs in a user and returns an access and refresh token",
        responses={
            200: "Login successful",
            400: "Bad Request",
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data
        if not user.email_verified:
            return Response({
                'message': 'Your email address has not been verified. Please check your inbox for the verification email or use the Resend Verification option if needed.',
                'status': 'unverified',
            }, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        return Response({
            "message": "Logged in successfully",
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        })


class ResendOTPView(views.APIView):
    """
    Resends the OTP to the user
    """
    serializer_class = ResendOTPSerializer
    permission_classes = []

    @swagger_auto_schema(
        tags=['Authentication'],
        request_body=serializer_class,
        operation_summary='Resend OTP',
        operation_description='Resends the OTP to the user',
        responses={
            200: 'OTP resent successfully',
            400: 'Bad Request',
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.account
        otp_obj = Otp.generate_otp(user=user)
        send_verification_email(
            name=user.name,
            email=user.email,
            otp=otp_obj.otp
        )

        return Response({'message': 'OTP resent successfully'}, status=status.HTTP_200_OK)


class ForgottenPasswordView(views.APIView):
    """
    Sends a password reset email to the user
    """
    serializer_class = ForgottenPasswordSerializer
    permission_classes = []

    @swagger_auto_schema(
        tags=['Authentication'],
        request_body=serializer_class,
        operation_summary='Request password reset',
        operation_description='Sends a password reset email to the user',
        responses={
            200: 'Password reset email sent to <email>',
            400: 'Bad Request',
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = get_object_or_404(Account, email=email)
        otp_obj = Otp.generate_otp(user=user)

        send_password_reset_email(
            email=user.email,
            code=otp_obj.otp
        )

        return Response({ 'message': f'Password reset email sent to {email}' }, status=status.HTTP_200_OK)


class ResetPasswordView(views.APIView):
    """
    Resets the user's password
    """
    serializer_class = ResetPasswordSerializer
    permission_classes = []

    @swagger_auto_schema(
        tags=['Authentication'],
        request_body=serializer_class,
        operation_summary='Reset password',
        operation_description='Resets the user\'s password',
        responses={
            200: 'Password reset successfully',
            400: 'Bad Request',
        },
    )
    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data['password']
        user = serializer.validated_data['code']
        if not user:
            return Response({ 'message': 'Invalid or expired reset token' }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()

        return Response({ 'message': 'Your password has been reset successfully' }, status=status.HTTP_200_OK)


class OTPVerificationView(views.APIView):
    """
    Verifies an account by validating an OTP
    """
    serializer_class = OTPVerificationSerializer
    permission_classes = []

    @swagger_auto_schema(
        tags=["Authentication"],
        request_body=serializer_class,
        operation_summary="Verify OTP",
        operation_description="Verifies an account by validating an OTP",
        responses={
            200: "OTP Verified successfully",
            400: "Bad Request",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        account = validated_data['user']

        # set email as verified
        account.email_verified = True
        account.save()

        refresh = RefreshToken.for_user(account)
        access_token = str(refresh.access_token)

        return Response({
            'message': 'OTP Verified successfully',
            "tokens": {
                "access_token": access_token,
                "refresh_token": str(refresh)
            }
        })


class RefreshTokenView(views.APIView):
    permission_classes = []
    serializer_class = LogoutSerializer
 
    @swagger_auto_schema(
        tags=["Authentication"],
        request_body=serializer_class,
        operation_summary="Refresh token",
        operation_description="Refreshes the access token using the refresh token",
        responses={
            200: "Token refreshed successfully",
            400: "Bad Request",
            500: "An error occurred while refreshing token",
        },
    )
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({ 'message': 'Refresh token not included' }, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            return Response({'access_token': access_token})
        except InvalidToken as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': f'An error occurred while refreshing token: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(views.APIView):
    permission_classes = []
    serializer_class = LogoutSerializer

    @swagger_auto_schema(
        tags=["Authentication"],
        request_body=serializer_class,
        operation_summary="Logout",
        operation_description="Logs out a user by blacklisting their refresh token",
        responses={
            200: "Successfully logged out",
            400: "Bad Request",
            500: "Could not log out",
        },
    )
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({ 'message': 'Refresh token not included' }, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()

            return Response({'message': 'Succesfully Logged out'}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({'message': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({ 'message': 'Could not log out' }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class GoogleAuthentication(views.APIView):
    permission_classes = []
    serializer_class = GoogleSocialAuthSerializer

    @swagger_auto_schema(
        tags=["Authentication"],
        request_body=serializer_class,
        operation_summary="Google Login",
        operation_description="Logs in / Register a user and returns an access and refresh token",
        responses={
            200: "Login successful",
            400: "Bad Request",
        },
    )
    def post(self,request,*args, **kwargs):

        """Send an ID token from google to get user information"""

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            print(data)
            return Response({
            "message": "Logged in successfully",
            "data": data["auth_token"],
            # "tokens": {
            #     "access_token": data["auth_token"]["access_token"],
            #     "refresh_token": data["auth_token"]["refresh_token"]
            # }
        })
