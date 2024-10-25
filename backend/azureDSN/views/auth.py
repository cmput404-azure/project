from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)

            response = Response({
                'is_authenticated': True,
                'user': {
                    'username': request.user.username,
                    'uuid': request.user.uuid,
                    'profileImage': request.user.profile_image.url if request.user.profile_image else None
                }
            }, status=status.HTTP_200_OK)
            response.set_cookie('sessionid', request.session.session_key, samesite='lax')

            return response
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        name = data.get('name')

        # username should be unique but display name (name) can be non-unique
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)

        # Create new user
        user = User.objects.create_user(username=username, password=password, email=email, display_name=name)
        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
    
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
                    'username': request.user.username,
                    'uuid': request.user.uuid,
                    'profileImage': request.user.profile_image.url if request.user.profile_image else None
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response({'is_authenticated': False}, status=status.HTTP_200_OK)