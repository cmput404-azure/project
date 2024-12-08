
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from django.core.validators import URLValidator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from urllib.parse import urlparse
from ..models.user import NodeUser, User
from ..serializers import NodeSerializer, NodeWithAuthenticationSerializer

class GetNodesView(APIView):
    @extend_schema(
        summary="Fetch the list of Nodes.",
        description="Fetch a list of all nodes (NodeUser entries), including their host, username, password, and authentication status.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="A list of Node users retrieved successfully.",
                response={
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "host": {"type": "string", "example": "http://example.com"},
                            "username": {"type": "string", "example": "node1"},
                            "password": {"type": "string", "example": "securepassword123"},
                            "is_authenticated": {"type": "boolean", "example": True},
                        }
                    }
                }
            ),
        },
        tags=["Node API"]
    )
    def get(self, request):
        """
            Fetch the list of `NodeUser` table.
        """
        # We only want to display these in the frontend
        node_users = NodeUser.objects.values('host', 'username', 'password', 'is_authenticated')

        # List of dictionaries automatically converted into JSON by DRF
        return Response(node_users, status=status.HTTP_200_OK)


class UpdateNodeView(APIView):
    @extend_schema(
        summary="Update details of a Node.",
        description="Update an existing NodeUser object by providing the `host`, `username`, `password`, and `is_authenticated` fields.",
        request=NodeWithAuthenticationSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="Node updated successfully.",
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "Node updated successfully!"}
                    }
                }
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid input or missing required fields.",
                response={
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Host is required."}
                    }
                }
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Node not found.",
                response={
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Node not found."}
                    }
                }
            ),
        },
        tags=["Node API"]
    )
    def put(self, request):
        """
            Edit a single `NodeUser` entry in the database.
        """
        try:
            host = request.data.get('host')
            username = request.data.get('username')
            password = request.data.get('password')
            is_auth = request.data.get('isAuth')
            old_host = request.data.get('oldHost')

            if not old_host:
                return Response({'error': 'Old host is required to locate the node.'}, status=status.HTTP_400_BAD_REQUEST)

            if not host:
                return Response({'error': 'Host is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if is_auth not in [True, False]:
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

            node_obj = get_object_or_404(NodeUser, host=old_host)
            node_obj.host = host
            node_obj.username = username
            node_obj.password = password
            node_obj.is_authenticated = is_auth
            node_obj.save()

            return Response({"message": "Node updated successfully!"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Unable to edit node: {str(e)}")
            return Response({"error": "Failed to update node. Please try again later."}, status=500)

class AddNodeView(APIView):
    @extend_schema(
        summary="Adds a new Node.",
        description="Create a new NodeUser object by providing the `host`, `username`, and `password`. The `is_authenticated` status defaults to True.",
        request=NodeSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                description="Node created successfully.",
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "Node added successfully"}
                    }
                }
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid input or missing required fields.",
                response={
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Missing required fields."}
                    }
                }
            ),
        },
        tags=["Node API"]
    )
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

class DeleteNodeView(APIView):    
    @extend_schema(
        summary="Delete a Node.",
        description="Remove a NodeUser object from the system by providing the `username` of the node to be deleted.",
        parameters=[
            OpenApiParameter(
                name="username",
                description="The `username` of the node to be deleted.",
                type=str,
                required=True,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="Node deleted successfully.",
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "Node removed successfully"}
                    }
                }
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Missing required field (username).",
                response={
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Missing required field."}
                    }
                }
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Node not found.",
                response={
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Node not found."}
                    }
                }
            ),
        },
        tags=["Node API"]
    ) 
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
        
