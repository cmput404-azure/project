from urllib.parse import urlparse
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models.site_config import SiteConfiguration
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = User.objects.get(username=username)
            site_config = SiteConfiguration.objects.first()

            # If approval is no longer required, activate the user automatically
            if not site_config.require_approval and not user.is_active:
                user.is_active = True
                user.save()

            # by default set to not active when they registered their account while the requires_approval setting is active
            elif site_config.require_approval and not user.is_active:
                return Response(
                    {'message': 'Your account is pending approval.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        except User.DoesNotExist:
            return Response(
                {'message': 'Login failed. Please check your credentials.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            response = Response({
                'is_authenticated': True,
                'user': {
                    'username': request.user.username,
                    'uuid': request.user.uuid,
                    'profileImage': request.user.profile_image if request.user.profile_image else None
                }
            }, status=status.HTTP_200_OK)
            response.set_cookie('sessionid', request.session.session_key, samesite='lax')

            return response
        
        return Response({'message': 'Login failed. Please check your credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
    

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        name = data.get('name')
        host = data.get('host')
        githubUsername = data.get('githubUsername')
        githubUrl = f"https://github.com/{githubUsername if githubUsername else 'login'}"

        base_host = host.rstrip('/api/')
        parsed_host = urlparse(host)
        if parsed_host.netloc == "localhost:3000" or parsed_host.netloc == "127.0.0.1:3000":
            host = "http://localhost:8000/api/" # when creating user locally, automatically change it to port 8000 so the API works

        config = SiteConfiguration.objects.first()
        is_active = not config.require_approval

        validate_url = URLValidator()
        try:
            validate_url(host)
        except ValidationError:
            return Response({"error": "Invalid URL format for host."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure host ends with /api/ -- for registration not on localhost
        if not host.endswith('/api/'):
            host = host.rstrip('/') + '/api/'

        # username should be unique but display name (name) can be non-unique
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)

        # Create new user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            display_name=name,
            github=githubUrl,
            host=host,
            is_active=is_active
        )

        user.page = f"{base_host}/authors/{user.uuid}" # use port 3000 if local
        user.save()
        
        if is_active:
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Registration pending approval."}, status=status.HTTP_201_CREATED)
    
class LogoutView(APIView):
    def get(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    
class CheckAuthView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            response = {
                'is_authenticated': True,
                'user': {
                    'host': request.user.host,
                    'username': request.user.username,
                    'uuid': request.user.uuid,
                    'profileImage': request.user.profile_image if request.user.profile_image else None,
                    'is_staff': request.user.is_staff
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response({'is_authenticated': False}, status=status.HTTP_200_OK)