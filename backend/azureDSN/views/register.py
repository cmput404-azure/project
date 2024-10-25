from rest_framework.views import APIView
from ..models import User
from rest_framework.response import Response
from rest_framework import status

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
