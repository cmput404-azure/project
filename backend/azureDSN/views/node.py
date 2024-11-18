
from urllib.parse import urlparse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from ..models.user import NodeUser, User
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError

class NodeView(APIView):
    def get(self, request):
        """
            Fetch the list of `NodeUser` table.
        """
        # We only want to display these in the frontend
        node_users = NodeUser.objects.values('host', 'username', 'password', 'is_authenticated')

        # List of dictionaries automatically converted into JSON by DRF
        return Response(node_users, status=status.HTTP_200_OK)
    
    def put(self, request):
        """
            Edit a single `NodeUser` entry in the database.
        """
        host = request.data.get('host')
        username = request.data.get('username')
        password = request.data.get('password')
        status = request.data.get('is_authenticated')

        if not host:
            return Response({'error': 'Host is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if status not in [True, False]:
            return Response({"error": "Status must be boolean."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        url_validator = URLValidator()
        try:
            url_validator(host)
        except DjangoValidationError:
            return Response({"error": "Invalid URL for host."}, status=status.HTTP_400_BAD_REQUEST)
        
        parsed_url = urlparse(host)
        if not parsed_url.scheme:
            host = f'http://{host}'

        try:
            url_validator(host)
        except DjangoValidationError:
            return Response({"error": "Invalid URL after adding scheme."}, status=status.HTTP_400_BAD_REQUEST)

        node_obj = get_object_or_404(NodeUser, host=host)
        node_obj.host = host
        node_obj.username = username
        node_obj.password = password
        node_obj.is_authenticated = status
        node_obj.save()

        return Response({"message": "Node updated successfully!"}, status=status.HTTP_200_OK)
    
    def post(self, request):
        """
            Add a node to NodeUser by providing the node's URL, username, and password.
        """
        username = request.data.get('username')
        password = request.data.get('password')
        node_url = request.data.get('host')

        if not username or not password or not node_url:
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists(): # Since NodeUser inherits from User
            return Response({"error": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)
    
        # Should check if node_url is proper URL
        url_validator = URLValidator()
        try:
            url_validator(node_url)
        except DjangoValidationError:
            return Response({"error": "Invalid URL."}, status=status.HTTP_400_BAD_REQUEST)
        
        parsed_url = urlparse(node_url)
        if not parsed_url.scheme:
            node_url = f'http://{node_url}'

        try:
            url_validator(node_url)
        except DjangoValidationError:
            return Response({"error": "Invalid URL after adding scheme."}, status=status.HTTP_400_BAD_REQUEST)

        node, created = NodeUser.objects.get_or_create(
            host=node_url,
            defaults={'username': username, 'password': password}
        )

        if created:
            return Response({'message': 'Node added successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Node already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
        """
            Remove a node from NodeUser (hard-delete).
        """
        # Updated call: http://localhost:8000/api/nodes/remove/?username=nodename
        node_name = request.query_params.get('username')

        if not node_name:
            return Response({'error': 'Missing required field.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            node = NodeUser.objects.get(username=node_name)
            node.delete()

            return Response({'message': 'Node removed successfully'}, status=status.HTTP_200_OK)
        except NodeUser.DoesNotExist:
            return Response({'error': 'Node not found.'}, status=status.HTTP_404_NOT_FOUND)
        