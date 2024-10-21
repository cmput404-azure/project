from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from ..models import User, Post
from ..serializers import UserSerializer, PostSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import status

class AuthorsPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'size'
    max_page_size = 100

class AuthorsView(APIView):
    pagination_provider  = AuthorsPagination
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
        tags=['Authors API']
    )
    def get(self, request, author_serial=None, author_fqid=None):
        """
        GET [local, remote] get the public authors
        """
        if(author_serial):
            # if uuid provided
            print(author_serial)
            author = get_object_or_404(User, uuid=author_serial)
            
            serializer = UserSerializer(author)
            return Response(serializer.data, status=200)
        elif(author_fqid):
            # if fqid provided
            print(author_fqid)

            # TODO: In future need to send request to remote server to get author
            author = get_object_or_404(User, uuid=author_fqid)

            serializer = UserSerializer(author)
            return Response(serializer.data, status=200)
        else:
            # Default behavior to return all authors
            authors = User.objects.all()
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
        tags=["Authors API"]
    )
    def put(self, request, author_serial=None):
        """
        PUT [local]: update a particular author's profile
        """

        print("Received request data:", request.data)
        author = get_object_or_404(User, uuid=author_serial)
        serializer = UserSerializer(author, data=request.data) # Send the whole JSON object everytime so partial won't be True

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)
    

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
        authors = User.objects.all()
        serializer = UserSerializer(authors, many=True)
        return Response(serializer.data, status=200)
