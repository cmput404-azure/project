from django.conf import settings
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from ..models import Post, Like, User, Comment
from ..serializers import LikeSerializer
from rest_framework.response import Response
from uuid import UUID
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from ..utils import url_parser
import requests, os
from requests.auth import HTTPBasicAuth

class LikesPagination(PageNumberPagination):
    page_size=10
    page_size_query_param='size'
    max_page_size=100

    def get_paginated_response(self, data):
        return Response({
            "type": "likes",
            "id": self.request.build_absolute_uri(),
            "page": '/'.join(self.request.build_absolute_uri().split('/')[:-1]),
            "page_number": self.page.number,
            "size": self.page.paginator.per_page,
            "count": self.page.paginator.count,
            "src": data,
        })

class LikeView(APIView):
    @extend_schema(
            summary="Retrieve a Like",
            description="Retrieve a specific Like object by `like_fqid` or a combination of `like_serial` and `author_serial`. Returns a 404 if not found.",
            parameters=[
                OpenApiParameter(
                    name='like_serial',
                    description='UUID of the Like to retrieve',
                    type=str,
                    required=False,
                    location=OpenApiParameter.PATH 
                ),
                OpenApiParameter(
                    name='author_serial',
                    description='UUID of the Author of the Like to retrieve',
                    type=str,
                    required=False,
                    location=OpenApiParameter.PATH
                ),
                OpenApiParameter(
                    name='like_fqid',
                    description='FQID of the Like to retrieve',
                    type=str,
                    required=False,
                    location=OpenApiParameter.PATH 
                ),
            ],
            responses={
                status.HTTP_200_OK: OpenApiResponse(response=LikeSerializer, description='Like retrieved successfully'),
                status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Like or Author not found.'),
                status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Invalid Like FQID or Like Serial or Author Serial'),
            },
            tags=['Likes & Liked API']
    )
    def get(self, request, like_fqid=None, author_serial=None, like_serial=None):
        """Handle retrieval of a single like."""
        try:
            if (author_serial and like_serial):
                """
                URL: ://service/api/authors/{AUTHOR_SERIAL}/liked/{LIKE_SERIAL}
                GET [local, remote] a single like
                Returns: like object
                """
                try:
                    author = User.objects.get(uuid=author_serial)
                    like = Like.objects.get(uuid=like_serial)
                except User.DoesNotExist:
                    return Response(
                        {"detail": "Author not found."}, status=status.HTTP_404_NOT_FOUND
                    )
                except Like.DoesNotExist:
                    return Response(
                        {"detail": "Like not found."}, status=status.HTTP_404_NOT_FOUND
                    )
            
            elif (like_fqid):
                """
                URL: ://service/api/liked/{LIKE_FQID}
                GET [local] a single like
                Returns: like object
                """
                try:
                    like_fqid = url_parser.percent_decode(like_fqid)
                    like_serial = url_parser.extract_uuid(like_fqid)
                    UUID(like_serial)
                    like = Like.objects.get(uuid=like_serial)
                except (IndexError, ValueError):
                    return Response(
                        {"detail": "Invalid Like FQID."}, status=status.HTTP_400_BAD_REQUEST
                    )

            else:
                return Response(
                    {"detail": "At least one of like_fqid or both author_serial and like_serial must be provided."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            serialized_like = LikeSerializer(like).data
            return Response(serialized_like, status=status.HTTP_200_OK) # for consistency with drf-spectacular
        
        except Exception as e:
            print(f"ERROR: {str(e)}")
            return Response({"detail": "An error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class AuthorLikesView(APIView):
    pagination_provider = LikesPagination

    @extend_schema(
            summary="Retrieve Likes by an Author.",
            description="Retrieve the latest 5 Like objects by `author_serial` or `author_fqid`.",
            parameters=[
                OpenApiParameter(
                    name='author_serial',
                    description='UUID of the Author whose Likes we want to retrieve',
                    type=str,
                    required=False,
                    location=OpenApiParameter.PATH
                ),
                OpenApiParameter(
                    name='author_fqid',
                    description='FQID of the Author whose Likes we want to retrieve',
                    type=str,
                    required=False,
                    location=OpenApiParameter.PATH 
                ),
            ],
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                    description="A response containing a list of likes.",
                    response={
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "example": "likes"},
                            "id": {"type": "string", "example": "https://service/api/authors/author-uuid/likes/"},
                            "page": {"type": "string", "example": "https://service/api/authors/author-uuid/likes/"},
                            "page_number": {"type": "integer", "example": 1},
                            "size": {"type": "integer", "example": 50},
                            "count": {"type": "integer", "example": 3},
                            "src": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/components/schemas/Like"  # Reference to LikeSerializer schema
                                }
                            }
                        }
                    }
                ),
                status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                    description='Invalid Author UUID or FQID'
                )
            },
            tags=['Likes & Liked API']
    )
    def get(self, request, author_serial=None, author_fqid=None):
        if (author_serial):
            """
            URL: ://service/api/authors/{AUTHOR_SERIAL}/liked
            GET [local, remote] a list of likes by AUTHOR_SERIAL
            Returns: likes object
            """
            author = get_object_or_404(User, uuid=author_serial)
            likes = Like.objects.filter(user__id=str(author.uuid)).order_by('-created_at')

        else:
            """
            URL: ://service/api/authors/{AUTHOR_FQID}/liked
            GET [local] a list of likes by AUTHOR_FQID
            Returns: likes object
            """
            try:
                author_serial = author_fqid.split('/')[-1]
                UUID(author_serial)
            except (IndexError, ValueError):
                return Response(
                    {"detail": "Invalid Author FQID."}, status=400
                )
            
            author = get_object_or_404(User, uuid=author_serial)
            likes = Like.objects.filter(user__id=str(author.uuid)).order_by('-created_at')


        pagination = self.pagination_provider()
        page = pagination.paginate_queryset(likes, request)

        serialized_likes = LikeSerializer(page, many=True).data

        return pagination.get_paginated_response(serialized_likes) # auto returns status code


class LikesView(APIView):
    pagination_provider = LikesPagination
    @extend_schema(
            summary="Retrieve Likes of a Post or Comment (TBD).",
            description="Retrieve multiple Like objects of a Post by `post_fqid` or a combination of `author_serial` or `post_serial`. This endpoint is also used to retrieve Likes of a Comment by FQID.",
            parameters=[
                OpenApiParameter(
                    name='author_serial',
                    description='UUID of the Author whose Likes we want to retrieve',
                    type=str,
                    required=False,
                    location=OpenApiParameter.PATH
                ),
                OpenApiParameter(
                    name='post_fqid',
                    description='FQID of the Post whose Likes we want to retrieve',
                    type=str,
                    required=False,
                    location=OpenApiParameter.PATH 
                ),
                OpenApiParameter(
                    name='post_serial',
                    description='UUID of the Post whose Likes we want to retrieve',
                    type=str,
                    required=False,
                    location=OpenApiParameter.PATH 
                ),
                OpenApiParameter(
                    name='comment_fqid',
                    description='FQID of the Comment whose Likes we want to retrieve',
                    type=str,
                    required=False,
                    location=OpenApiParameter.PATH 
                ),
            ],
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                    description="A response containing a list of likes.",
                    response={
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "example": "likes"},
                            "id": {"type": "string", "example": "https://service/api/authors/author-uuid/posts/post-uuid/likes"},
                            "page": {"type": "string", "example": "https://service/api/authors/author-uuid/posts/post-uuid"},
                            "page_number": {"type": "integer", "example": 1},
                            "size": {"type": "integer", "example": 50},
                            "count": {"type": "integer", "example": 3},
                            "src": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/components/schemas/Like"  # Reference to LikeSerializer schema
                                }
                            }
                        }
                    }
                ),
                status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Either Post, Author, or Comment not found.'),
                status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Invalid Post FQID.'),
            },
            tags=['Likes & Liked API']
    )
    def get(self, request, author_serial=None, post_serial=None, post_fqid=None, comment_fqid=None):
        if (comment_fqid and author_serial and post_serial):
            """
            URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments/{COMMENT_FQID}/likes
            GET [local, remote] a list of likes from other authors on AUTHOR_SERIAL's post POST_SERIAL comment COMMENT_FQID
            Return: likes object
            """

            # Example of comment_fqid would be like http://localhost:8000/authors/1234-abcd-efgh-5678/comments/0000-0001-0002-1000
            try:
                path_parts = comment_fqid.strip('/').split('/')
                
                comment_serial = path_parts[-1]
                UUID(comment_serial) # will raise error if not UUID

            except (IndexError, ValueError):
                return Response(
                    {"detail": "Invalid FQID."}, status=400
                )

            type = "commented"
            post = get_object_or_404(Post, uuid=post_serial)
            author = get_object_or_404(User, uuid=author_serial)
            comment = get_object_or_404(Comment, comment_id=comment_serial)

            # Liking a comment functionality not handled right now...
        
        elif (author_serial and post_serial):
            """
            URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/likes
            GET [local, remote] a list of likes from other authors on AUTHOR_SERIAL's post POST_SERIAL
            Return: likes object
            """
            type = "posts"

            try:
                author = User.objects.get(uuid=author_serial)
                post = get_object_or_404(Post, uuid=post_serial, user=author)
                likes = Like.objects.filter(post=post).order_by('-created_at')

            except User.DoesNotExist:
                # Remote scenario
                author_fqid = request.GET.get('authorId')

                if not author_fqid:
                    return Response(
                        {"error": "Missing 'authorId' query parameter."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                author_fqid = url_parser.percent_decode(author_fqid)
                author_host = url_parser.get_base_host(author_fqid)

                if settings.BASE_URL in author_host:
                    # Local scenario but the serial is invalid
                    return Response({"error": "Invalid serial."}, status=status.HTTP_404_NOT_FOUND)

                author_serial = url_parser.extract_uuid(author_fqid)

                endpoint = f"{author_host}/api/authors/{author_serial}/posts/{post_serial}/likes"

                response = requests.get(
                    endpoint,
                    auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD')),
                    timeout=5
                )

                if response.status_code == 200:
                    return Response(response.json(), status=status.HTTP_200_OK)
                
                else:
                    return Response(
                        {"error": f"Failed to fetch remote likes: {response.status_code}"},
                        status=response.status_code
                    )


        elif (post_fqid):
            """
            URL: ://service/api/posts/{POST_FQID}/likes
            GET [local] a list of likes from other authors on AUTHOR_SERIAL's post POST_SERIAL
            Return: likes object
            """
            type = "posts"
            try:
                # Example: "/api/posts/{POST_SERIAL}"
                path_parts = post_fqid.strip('/').split('/')
                
                post_serial = path_parts[-1]
                UUID(post_serial) # will raise error if not UUID

            except (IndexError, ValueError):
                return Response(
                    {"detail": "Invalid FQID."}, status=400
                )
            
            post = get_object_or_404(Post, uuid=post_serial)
            likes = Like.objects.filter(post=post).order_by('-created_at')
            count = Like.objects.filter(post=post).count()
            author_serial = post.user.uuid

        pagination = self.pagination_provider()
        page = pagination.paginate_queryset(likes, request)

        serialized_likes = LikeSerializer(page, many=True).data

        return pagination.get_paginated_response(serialized_likes) # auto returns status code

