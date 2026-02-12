from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.serializers import UserSerializer
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

class CustomTokenObtainPairView(TokenObtainPairView):
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