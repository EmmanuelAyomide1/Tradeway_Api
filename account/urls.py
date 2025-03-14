from django.urls import path
from .views import (
  SignUpView,
  LoginView,
  LogoutView,
  RefreshTokenView,
  OTPVerificationView,
  ResendOTPView,
  ResetPasswordView,
  ForgottenPasswordView,
  GoogleAuthentication
  )


urlpatterns = [
    path("signup", SignUpView.as_view(), name="signup"),
    path("login", LoginView.as_view(), name="login"),
    path("refresh-token", RefreshTokenView.as_view(), name="refresh-token"),
    path("verify-otp", OTPVerificationView.as_view(), name="verify-otp"),
    path("resend-otp", ResendOTPView.as_view(), name="resend-otp"),
    path("reset-password", ResetPasswordView.as_view(), name="reset-password"),
    path("forgot-password", ForgottenPasswordView.as_view(), name="forgot-password"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("social_login/google",GoogleAuthentication.as_view(), name="social-google")
]