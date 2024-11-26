from requests.auth import HTTPBasicAuth
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from ..models import User
from ..serializers import UserSerializer
from ..utils import url_parser
from urllib.parse import urlparse
from uuid import UUID
import requests, os

class AuthorsPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'size'
    max_page_size = 100

class AuthorsView(APIView):
    pagination_provider  = AuthorsPagination
   
    @extend_schema(
        summary="Retrieve all authors with page options",
        description="Retrieve an author by UUID or all authors on the node",
        parameters=[
            OpenApiParameter(
                name="page",
                description="Page number",
                required=False,
                type=int
            ),
            OpenApiParameter(
                name="size",
                description="Number of items per page",
                required=False,
                type=int
            )
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description='Author(s) retrieved successfully.',
                response=UserSerializer,
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description='Author not found.'
            )
        },
        operation_id='get_author',
        tags=['Authors API']
    )
    def get(self, request):
        """
        GET [local, remote] get all authors on the node
        """
        authors = User.objects.filter(type="author").order_by('-created_at')
        pagination = self.pagination_provider()
        page = pagination.paginate_queryset(authors, request)

        serializer = UserSerializer(page, many=True)
        authors_serialized = serializer.data

        authors = []
        for author in authors_serialized:
            authors.append(author)

        return Response({
            "type": "authors",
            "authors": authors
        }, status=200)

class AuthorsSpecificView(APIView):
    @extend_schema(
        summary="Retrieve an author or all authors",
        description=(
            "Retrieve a specific author by `author_serial` (UUID) or `author_fqid` -- Example output is 'Single Author Example'.\n"
            "If no parameters are provided, all authors on the node will be returned -- Example output is 'All Author Example'."
        ),
        parameters=[
            OpenApiParameter(
                name='author_serial',
                description='UUID of the author to retrieve.',
                type=str,
                required=False,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name='author_fqid',
                description='FQID of the author to retrieve (optional).',
                type=str,
                required=False,
                location=OpenApiParameter.PATH
            )
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description='Author(s) retrieved successfully.',
                response=UserSerializer,
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description='Author not found.'
            )
        },
        operation_id='get_author',
        tags=['Authors API']
    )
    def get(self, request, author_fqid=None, author_serial=None ):
        """
        GET [local, remote] get the public authors
        """

        if (author_serial):
            author = get_object_or_404(User, uuid=author_serial)
            serializer = UserSerializer(author)
            return Response(serializer.data, status=200)
        
        elif (author_fqid):
            author_serial = url_parser.extract_uuid(author_fqid) # cornflowerblue uses integer, so don't check for UUID
            base_host = url_parser.get_base_host(author_fqid)

            if base_host.strip().lower() == os.getenv('BASE_URL', 'http://localhost:8000').strip().lower():
                local_user = get_object_or_404(User, uuid=author_serial)
                serializer = UserSerializer(local_user)
                return Response(serializer.data, status=200)

            try:
                # Send request to remote server to get remote author's info
                remote_author_url = f"{base_host}/api/authors/{author_serial}/"
                response = requests.get(
                    remote_author_url,
                    auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD')),
                )
                if response.status_code == 200:
                    return Response(response.json(), status=status.HTTP_200_OK)
                else:
                    return Response({"error": f"Failed to fetch author: {response.text}"}, status=response.status_code)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Update Author Profile",
        description="Update the profile of a specific author identified by `author_serial`. You must provide the full author data in the request body.",
        parameters=[
            OpenApiParameter(
                name='author_serial',
                description='UUID of the Author to update',
                type=str,
                required=True,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name='author_fqid',
                description='FQID of the Author to update',
                type=str,
                required=True,
                location=OpenApiParameter.PATH
            )
        ],
        request=UserSerializer,
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description="Author profile updated successfully."
            ),
            400: OpenApiResponse(
                description="Invalid input data or validation errors.",
                examples={
                    "error_example": {
                        "summary": "Validation Error Example",
                        "value": {
                            "username": ["This field is required."],
                            "email": ["Enter a valid email address."]
                        }
                    }
                }
            ),
            404: OpenApiResponse(description="Author not found.")
        },
        operation_id='update_author',
        tags=["Authors API"]
    )
    def put(self, request, author_serial=None, author_fqid=None):
        """
        PUT [local]: update a particular author's profile
        """
        if(author_serial):
            author = get_object_or_404(User, uuid=author_serial)
            serializer = UserSerializer(author, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
        elif(author_fqid):
            author_serial = author_fqid.split('/')[-1]
            UUID(author_serial)
            author = get_object_or_404(User, uuid=author_serial)
            serializer = UserSerializer(author, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)
    
    @extend_schema(exclude=True)  # Hide this method from Swagger
    def put_no_params(self, request):
        """
        PUT [no params]: This method will not appear in the Swagger docs.
        """
        return Response(status=405)

class AuthorsCompleteView(APIView):
    @extend_schema(
        summary="Retrieve all local authors",
        description="This endpoint returns a list of all authors present in the local node.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="A list of all local authors.",
                response={
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "example": "authors"
                        },
                        "authors": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "example": "author"
                                    },
                                    "id": {
                                        "type": "string",
                                        "example": "http://nodeaaaa/api/authors/111"
                                    },
                                    "host": {
                                        "type": "string",
                                        "example": "http://nodeaaaa/api/"
                                    },
                                    "displayName": {
                                        "type": "string",
                                        "example": "Greg Johnson"
                                    },
                                    "github": {
                                        "type": "string",
                                        "example": "http://github.com/gjohnson"
                                    },
                                    "profileImage": {
                                        "type": "string",
                                        "example": "https://i.imgur.com/k7XVwpB.jpeg"
                                    },
                                    "page": {
                                        "type": "string",
                                        "example": "http://nodeaaaa/authors/greg"
                                    }
                                }
                            }
                        }
                    }
                }
            )
        },
        tags=["Authors API"]
    )
    def get(self, request):
        """
        Gets all the author in our local node.
        """
        user_uuid = request.query_params.get('user')

        users = []
        if user_uuid == 'anonymous':
            local_users = User.objects.filter(type="author")
            local_serializer = UserSerializer(local_users, many=True)
            users.extend(local_serializer.data)
        else:
            # Query all users of type 'author' and exclude the current user
            local_users = User.objects.exclude(uuid=user_uuid).filter(type="author")
            local_serializer = UserSerializer(local_users, many=True)
            users.extend(local_serializer.data)

            remote_node = User.objects.filter(type="node")
            for node in remote_node:
                parsed_url = urlparse(node.host)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                api_url = f"{base_url}/api/authors/"

                try:
                    response = requests.get(
                        api_url,
                        auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD'))
                    )

                    if response.status_code == 403:
                        continue

                    data = response.json()

                    if "authors" in data and data["authors"]:
                        users.extend(data["authors"])
                    else:
                        continue
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching authors from node {node.host}: {e}")
                    continue
                
        return Response(users, status=200)
