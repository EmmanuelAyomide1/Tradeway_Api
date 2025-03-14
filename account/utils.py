import os

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from google.oauth2 import id_token
from google.auth.transport import requests as rqst

from .models import Account


class Google:
    """Google class to fetch the user info and return it"""

    @staticmethod
    def validate(auth_token):
        """
        validate method Queries the Google oAUTH2 api to fetch the user info
        """
        try:
            idinfo = id_token.verify_oauth2_token(
                auth_token, rqst.Request(), audience=os.environ.get("GOOGLE_CLIENT_ID")
            )

            if "accounts.google.com" in idinfo["iss"]:
                return idinfo

        except Exception as e:
            print('error',e)
            return "The token is either invalid or has expired"

def create_or_get_social_user(validated_data, auth_type):
    user = Account.objects.filter(email=validated_data.get("email")).first()
    if not user:
        user = Account.objects.create(**validated_data)
        user.set_password("")
        user.verified = True
        user.auth_type = auth_type
        user.save()

        # Create default models here
        # e.g Profile.objects.create(user=user)

    refresh_token = RefreshToken.for_user(user)
    access_token = AccessToken.for_user(user)
    return user, refresh_token, access_token
