import re

from decouple import config

from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from account.models import Account

from .models import Otp
from .utils import Google, create_or_get_social_user


class SignUpSerializer(serializers.ModelSerializer):
    account_type = serializers.ChoiceField(choices=Account.ACCOUNT_TYPES)
    email = serializers.EmailField()

    class Meta:
        model = Account
        fields = ["name", "email", "account_type", "password"]
        extra_kwargs = {
            "password": {"write_only": True},
        }
    
    def validate_email(self, value):
        if Account.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_password(self, password):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>])[A-Za-z\d!@#$%^&*(),.?\":{}|<>]{8,}$"
        if not re.match(pattern, password):
            raise serializers.ValidationError(
                'Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one digit and one special character'
                )            
        return password

    def create(self, validated_data):
        return Account.objects.create_user(**validated_data)


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        user = authenticate(**data)
        if user:
            return user
        raise serializers.ValidationError('Incorrect email or password')


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class OTPVerificationSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, attrs):
        code = attrs.get('code')

        try:
            otp = Otp.objects.get(otp=code)
            if otp.is_valid():
                # invalidate otp
                otp.use()

                attrs['user'] = otp.user
                return attrs
            else:
                raise serializers.ValidationError('Invalid OTP')

        except Exception as e:
            raise serializers.ValidationError(e)

        return attrs


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        try:
            self.account = Account.objects.get(email=email)
            if self.account.email_verified:
                raise serializers.ValidationError('Email already verified')
        except Account.DoesNotExist:
            raise serializers.ValidationError('Email does not exist')
        return email


class ForgottenPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    code = serializers.CharField()

    def validate_code(self, value):
        try:
            otp = Otp.objects.get(otp=value)
            if otp.is_valid():
                otp.use()
            else:
                raise serializers.ValidationError('Invalid OTP')
        except Exception as e:
            raise serializers.ValidationError('Invalid OTP')
        
        return otp.user

    def validate_password(self, password):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>])[A-Za-z\d!@#$%^&*(),.?\":{}|<>]{8,}$"
        if not re.match(pattern, password):
            raise serializers.ValidationError(
                'Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one digit and one special character'
                )            
        return password
    

class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = Google.validate(auth_token)
        try:
            user_data["sub"]
        except:
            raise serializers.ValidationError(
                " The token is invalid or expired. Please login again"
            )
        
        if user_data["aud"] != config("GOOGLE_CLIENT_ID"):
            raise AuthenticationFailed("User Not Recognized")

        email = user_data["email"]
        name = user_data["given_name"] if user_data["given_name"] else ""
        # lastname = user_data["family_name"] if user_data["family_name"] else ""
        auth_type = "google"
        user_info = {
            "name": name,
            "email": email,
        }

        user, refresh_token, access_token = create_or_get_social_user(
            user_info, auth_type
        )

        user_details = {}
        data = {}
        user_details["id"] = user.id
        user_details["email"] = user.email
        # user_details["account_type"] = user.account_type
        user_details["name"] = user.name

        data["user"] = user_details
        data["refresh_token"] = str(refresh_token)
        data["access_token"] = str(access_token)

        return data
    
class TokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    response_token = serializers.CharField()

class LoginResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    tokens =  TokenSerializer()