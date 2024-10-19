from rest_framework.views import APIView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse 
from ..models import Post, Like, User, Comment
from ..serializers import LikeSerializer
from rest_framework.response import Response
from uuid import UUID
from urllib.parse import urlparse, unquote
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import status

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
            }
    )
    def get(self, request, like_fqid=None, author_serial=None, like_serial=None):
        """Handle retrieval of a single like."""
        if (like_serial):
            """
            URL: ://service/api/authors/{AUTHOR_SERIAL}/liked/{LIKE_SERIAL}
            GET [local, remote] a single like
            Returns: like object
            """
            author = get_object_or_404(User, uuid=author_serial)
            like = get_object_or_404(Like, user__id = str(author.uuid), uuid=like_serial)
        
        elif (like_fqid):
            """
            URL: ://service/api/liked/{LIKE_FQID}
            GET [local] a single like
            Returns: like object
            """
            try:
                like_serial = like_fqid.split('/')[-1]
                UUID(like_serial)
            except (IndexError, ValueError):
                return Response(
                    {"detail": "Invalid Like FQID."}, status=status.HTTP_400_BAD_REQUEST
                )
            
            like = get_object_or_404(Like, uuid=like_serial)

        else:
            return Response(
                {"detail": "At least one of like_fqid or both author_serial and like_serial must be provided."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        serialized_like = LikeSerializer(like).data

        # Modify serialized data with absolute URIs
        uri = request.build_absolute_uri("/")
        serialized_like['id'] = uri + serialized_like['id']
        serialized_like['object'] = uri + serialized_like['object']

        return Response(serialized_like, status=status.HTTP_200_OK) # for consistency with drf-spectacular
    
    # @extend_schema(
    #     summary="Create a Like",
    #     description="Create a new Like for a Post by sending a Like object in the request body.",
    #     request=LikeSerializer,
    #     responses={
    #         status.HTTP_201_CREATED: 'Like created successfully',
    #         status.HTTP_400_BAD_REQUEST: 'Invalid data provided',
    #     }
    # )
    # def post(self, request, author_serial=None):
    #     """
    #     URL: ://service/api/authors/{AUTHOR_SERIAL}/inbox
    #     POST [remote]: send a like object to AUTHOR_SERIAL
    #     Payload: like object
    #     """
    #     data = request.data
    #     # unfinished -- Quin will handle Inbox

    
class AuthorLikesView(APIView):
    """
    Handle retrieval of Likes by an Author.
    """
    def get(self, request, author_serial=None, author_fqid=None):
        if (author_serial):
            """
            URL: ://service/api/authors/{AUTHOR_SERIAL}/liked
            GET [local, remote] a list of likes by AUTHOR_SERIAL
            Returns: likes object
            """
            author = get_object_or_404(User, uuid=author_serial)
            likes = Like.objects.filter(user__id=str(author.uuid)).order_by('-created_at')[:5] # Limit to latest 5 likes
            count = Like.objects.filter(user__id=str(author.uuid)).count()

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
            likes = Like.objects.filter(user__id=str(author.uuid)).order_by('-created_at')[:5]
            count = Like.objects.filter(user__id=str(author.uuid)).count()

        serialized_likes = LikeSerializer(likes, many=True).data

        uri = request.build_absolute_uri("/")

        response = {
            "type": "likes",
            "id": uri + f"api/authors/{author_serial}/likes/",
            "page": uri + f"api/authors/{author_serial}/likes/", # might need to implement this page to view all user likes
            "page_number": 1, # not sure what pagenum is for
            "size": 50, # don't really know what this is
            "count": count,
            "src": serialized_likes,
        }

        return Response(response, status=200)


class LikesView(APIView):
    """
    Handle retrieval of Likes on a Post or a Comment.
    """
    def get(self, request, author_serial=None, post_serial=None, post_fqid=None, comment_serial=None):
        if (comment_serial and author_serial and post_serial):
            """
            URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments/{COMMENT_SERIAL}/likes
            GET [local, remote] a list of likes from other authors on AUTHOR_SERIAL's post POST_SERIAL comment COMMENT_SERIAL
            Return: likes object
            """
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
            post = get_object_or_404(Post, uuid=post_serial)
            # author = get_object_or_404(User, uuid=author_serial)

            likes = Like.objects.filter(post=post).order_by('-created_at')[:5]
            count = Like.objects.filter(post=post).count()

        elif (post_fqid):
            """
            URL: ://service/api/posts/{POST_FQID}/likes
            GET [local] a list of likes from other authors on AUTHOR_SERIAL's post POST_SERIAL
            Return: likes object
            """
            type = "posts"
            try:
                # Parse and decode the URL to handle percent-encoding
                parsed_url = urlparse(post_fqid)
                path = unquote(parsed_url.path)

                # Example: "/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/"
                path_parts = path.strip('/').split('/')

                # Validate the path structure
                if len(path_parts) < 4 or path_parts[-2] != 'posts':
                    raise ValueError("Invalid FQID structure")

                # Extract AUTHOR_SERIAL and POST_SERIAL
                author_serial = path_parts[-4]
                post_serial = path_parts[-1]

                # Validate that both are UUIDs
                UUID(author_serial)
                UUID(post_serial)

            except (IndexError, ValueError):
                return Response(
                    {"detail": "Invalid FQID."}, status=400
                )
            
            post = get_object_or_404(Post, uuid=post_serial)
            author = get_object_or_404(User, uuid=author_serial)
            likes = Like.objects.filter(post=post).order_by('-created_at')[:5]
            count = Like.objects.filter(post=post).count()
            


        likes = LikeSerializer(likes, many=True).data

        uri = request.build_absolute_uri("/")

        response_data = {
            "type": "likes",
            "id": uri + f"api/authors/{author_serial}/{type}/{post_serial}/likes/",
            "page": uri + f"api/authors/{author_serial}/{type}/{post_serial}",
            "page_number": 1,
            "size": 50,
            "count": count,
            "src": likes
        }

        return Response(response_data, status=200)
