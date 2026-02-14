from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.serializers import UserSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import status
from .models import User
from .utils import generate_token


class RegisterView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered"}, status=400)

        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = serializer.save()
        user.is_active = False  # Deactivate account until email is confirmed
        user.save()

        # Email Logic
        current_site = get_current_site(request)
        subject = "Activate your AI Chatbot Account"
        message = render_to_string('activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user),
        })
        
        email_drive = EmailMessage(subject, message, to=[user.email])
        email_drive.send()

        return Response({"message": "Check your email to confirm registration."}, status=201)

def set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE'], 
        value=refresh_token,
        expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        path='/api/token/refresh/', # Security: only sent to the refresh endpoint
    )


def build_auth_response_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['is_superuser'] = user.is_superuser
    refresh['email'] = user.email

    response = Response({"access": str(refresh.access_token)}, status=status.HTTP_200_OK)
    set_refresh_cookie(response, str(refresh))
    return response

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh = response.data.pop('refresh')
            set_refresh_cookie(response, refresh)
        return response


class ActivateAccountView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Account activated successfully!"}, status=200)
        
        return Response({"error": "Activation link is invalid!"}, status=400)


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
            reset_url = f"{frontend_url}/?mode=reset&uid={uid}&token={token}"

            subject = 'Reset your password'
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })

            email_drive = EmailMessage(subject, message, to=[user.email])
            email_drive.content_subtype = "html"
            email_drive.send()

        return Response({"message": "If this email exists, a reset link has been sent."}, status=200)


class VerifyResetTokenView(APIView):
    def get(self, request):
        uidb64 = request.query_params.get('uid')
        token = request.query_params.get('token')

        if not uidb64 or not token:
            return Response({"error": "Missing reset token data."}, status=400)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid reset link."}, status=400)

        if default_token_generator.check_token(user, token):
            return Response({"message": "Reset token is valid."}, status=200)

        return Response({"error": "Reset token is invalid or expired."}, status=400)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        uidb64 = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['password']

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid reset link."}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Reset token is invalid or expired."}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successful. You can now log in."}, status=200)

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # The refresh token is automatically taken from the cookie by the middleware/helper
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        if refresh_token:
            request.data['refresh'] = refresh_token
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200 and 'refresh' in response.data:
            refresh = response.data.pop('refresh')
            set_refresh_cookie(response, refresh)
            
        return response
    
class LogoutView(APIView):
    def post(self, request):
        try:
            # 1. Get the refresh token from the cookie
            refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
            
            if refresh_token:
                # 2. Blacklist the token so it can't be used again
                token = RefreshToken(refresh_token)
                token.blacklist()

            # 3. Create response and clear the HttpOnly cookie
            response = Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
            response.delete_cookie(
                settings.SIMPLE_JWT['AUTH_COOKIE'],
                path='/api/token/refresh/' # Must match the path used during login
            )
            return response
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GoogleLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        credential = request.data.get('credential')
        client_id = str(getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', '')).strip().strip('"')

        if not client_id:
            return Response({"error": "Google OAuth is not configured on the server."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not credential:
            return Response({"error": "Missing Google credential token."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token_payload = id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                client_id,
            )
        except ValueError as oauth_error:
            try:
                token_payload = id_token.verify_token(
                    credential,
                    google_requests.Request(),
                )
            except ValueError as token_error:
                error_message = "Invalid Google token."
                if settings.DEBUG:
                    error_message = f"Invalid Google token: {token_error}"
                return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

            audience = token_payload.get('aud')
            authorized_party = token_payload.get('azp')

            audience_matches = audience == client_id or (
                isinstance(audience, list) and client_id in audience
            )
            azp_matches = authorized_party == client_id

            if not (audience_matches or azp_matches):
                error_message = "Google token audience does not match this app client."
                if settings.DEBUG:
                    error_message = (
                        f"Google token audience mismatch (aud={audience}, azp={authorized_party}, "
                        f"client_id={client_id}, oauth_error={oauth_error})."
                    )
                return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

            issuer = token_payload.get('iss')
            if issuer not in {'accounts.google.com', 'https://accounts.google.com'}:
                return Response({"error": "Invalid Google token issuer."}, status=status.HTTP_400_BAD_REQUEST)

        email = token_payload.get('email')
        if not email:
            return Response({"error": "Google account email is unavailable."}, status=status.HTTP_400_BAD_REQUEST)

        email_verified = token_payload.get('email_verified', False)
        if not email_verified:
            return Response({"error": "Google account email is not verified."}, status=status.HTTP_400_BAD_REQUEST)

        first_name = token_payload.get('given_name', '')
        last_name = token_payload.get('family_name', '')

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True,
            },
        )

        if created:
            user.set_unusable_password()
            user.save()
        else:
            updated_fields = []
            if not user.first_name and first_name:
                user.first_name = first_name
                updated_fields.append('first_name')
            if not user.last_name and last_name:
                user.last_name = last_name
                updated_fields.append('last_name')
            if not user.is_active:
                user.is_active = True
                updated_fields.append('is_active')
            if updated_fields:
                user.save(update_fields=updated_fields)

        return build_auth_response_for_user(user)