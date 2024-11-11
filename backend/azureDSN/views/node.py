from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models.user import NodeUser, User
from requests.auth import HTTPBasicAuth
import requests

class NodeView(APIView):
    def post(self, request):
        """
            Add a node to NodeUser by providing the node's URL, username, and password.
        """
        username = request.data.get('username')
        password = request.data.get('password')
        node_url = request.data.get('url')

        if not username or not password or not node_url:
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists(): # Since NodeUser inherits from User
            return Response({"error": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)
        
        # hashed_password = make_password(password) # if we want to hash the password, then uncomment this

        node, created = NodeUser.objects.get_or_create(
            host=node_url,
            defaults={'username': username, 'password': password}
        )

        if created:
            return Response({'message': 'Node added successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Node already exists'}, status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self, request):
        """
            Remove a node from NodeUser (hard-delete).
        """
        # Example call: http://localhost:8000/api/nodes/remove/?node=http://azuretest/api/
        node_url = request.query_params.get('node')

        if not node_url:
            return Response({'error': 'Missing required field.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            node = NodeUser.objects.get(host=node_url)
            node.delete()
            return Response({'message': 'Node removed successfully'}, status=status.HTTP_200_OK)
        except NodeUser.DoesNotExist:
            return Response({'error': 'Node not found.'}, status=status.HTTP_404_NOT_FOUND)


class NodeConnectionView(APIView):
    def post(self, request):
        """
            Establish a connection with remote nodes.
        """
        node_url = request.data.get('url')
        username = request.data.get('username')
        password = request.data.get('password')

        if not node_url or not username or not password:
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Send a test GET request to the remote node's API with basic auth
            response = requests.get(
                node_url,
                auth=HTTPBasicAuth(username, password),
                timeout=5
            )
            # Check if the connection is successful
            if response.status_code == 200:
                node = get_object_or_404(NodeUser, host=node_url)
                node.is_authenticated = True    # we've validated the credentials
                return Response({'message': 'Connected successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to connect'}, status=status.HTTP_401_UNAUTHORIZED)
        except requests.exceptions.RequestException as e:
            return Response({'error': f'Connection error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request):
        """
            Disable a connection with remote nodes by toggling is_authenticated flag off.
        """
        node_url = request.data.get('url')

        if not node_url:
            return Response({'error': 'Missing required field.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            node = NodeUser.objects.get(host=node_url)
            node.is_authenticated = False
            return Response({'message': 'Node connection deactivated.'}, status=status.HTTP_200_OK)
        except NodeUser.DoesNotExist:
            return Response({'error': 'Node not found.'}, status=status.HTTP_404_NOT_FOUND)