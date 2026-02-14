from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    ActivateAccountView,
    RegisterView,
    ForgotPasswordView,
    VerifyResetTokenView,
    ResetPasswordView,
    GoogleLoginView,
)

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/verify/', VerifyResetTokenView.as_view(), name='verify_reset_token'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('google-login/', GoogleLoginView.as_view(), name='google_login'),
    ]