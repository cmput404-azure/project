from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiTypes
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers
from requests.auth import HTTPBasicAuth
from ..serializers import *
from ..models import *
from ..utils import url_parser
import requests, os, uuid

class CommentsPagination(PageNumberPagination):
    page_size=5
    page_size_query_param='size'
    max_page_size=100

    def get_paginated_response(self, data):
        return Response({
            "type": "comments",
            "id": self.request.build_absolute_uri(),
            "page": self.request.build_absolute_uri(),
            "page_number": self.page.number,
            "size": self.page.paginator.per_page,
            "count": self.page.paginator.count,
            "src": data,
        })

'''
Handle retrieval of all the comments in a post
Both case return a comments object which is a list of comment object
'''
class MultipleCommentsView(APIView):
    pagination_provider = CommentsPagination


    @extend_schema(
        summary="Retrieve Comments for a Post",
        description="Fetches all comments on a specific post, optionally filtered by author.",
        parameters=[
            OpenApiParameter(
                name="author_serial",
                description="UUID of the author of the post.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name="post_serial",
                description="UUID of the post to retrieve comments for.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name="post_fqid",
                description="Full qualified identifier (FQID) of the post to retrieve comments for.",
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH
            )
        ],
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="PaginatedCommentsResponse",
                    fields={
                        "type": serializers.CharField(),
                        "id": serializers.CharField(),
                        "page": serializers.CharField(),
                        "page_number": serializers.IntegerField(),
                        "size": serializers.IntegerField(),
                        "count": serializers.IntegerField(),
                        "src": CommentSerializer(many=True),
                    }
                ),
                description="Paginated list of comments for the specified post."
            ),
            404: OpenApiResponse(description="Post or author not found.")
        }
    )

    def get(self, request, author_serial=None, post_serial=None, post_fqid=None):
        if (author_serial):
            '''
            URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments
            GET [local, remote]: the comments on the post
            '''
            post_id = post_serial
            post_obj = get_object_or_404(Post, uuid=post_serial, user__uuid=author_serial)
            comments = Comment.objects.filter(post=post_obj).order_by('-created_at')
            pagination = self.pagination_provider()
            page = pagination.paginate_queryset(comments, request)

            serialized_comments = CommentSerializer(page, many=True).data
            return pagination.get_paginated_response(serialized_comments)

        else:
            '''
            URL: ://service/api/posts/{POST_FQID}/comments
            vd:POST_FQID: http://nodebbbb/api/authors/222/posts/249
            GET [local, remote]: the comments on the post (that our server knows about)    
            '''
            post_fqid = url_parser.percent_decode(post_fqid)
            post_id = url_parser.extract_uuid(post_fqid)

            try:
                uuid.UUID(post_id)
            except ValueError:
                # If not a UUID, check if it's an integer
                if not post_id.isdigit():
                    return Response({"detail": "Invalid post identifier"}, status=400)

            try:
                post_obj = Post.objects.get(uuid=post_id)
                comments = Comment.objects.filter(post=post_obj).order_by('-created_at')
                pagination = self.pagination_provider()
                page = pagination.paginate_queryset(comments, request)

                serialized_comments = CommentSerializer(page, many=True).data
                return pagination.get_paginated_response(serialized_comments)

            except Post.DoesNotExist:
                remote_comments = []
                try:
                    # call remote endpoint
                    response = requests.get(
                        f"{post_fqid.rstrip('/')}/comments",
                        auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD'))
                    )

                    if response.status_code == 200:
                        remote_comments = response.json()
                        
                        # Return the paginated response directly
                        return Response(remote_comments, status=200)
                    
                    else:
                        return Response({"detail": "Unable to fetch remote comments."}, status=response.status_code)
                except Exception as e:
                    print(f"Something went wrong: {str(e)}")
                    return Response({"detail": "An internal server error occurred."}, status=500)
 

'''
URL: ://service/api/authors/{AUTHOR_SERIAL}/post/{POST_SERIAL}/comment/{REMOTE_COMMENT_FQID}
GET [local, remote] get the comment
'''  
class SingleCommentView(APIView):
    """Handle retrieval of a single comment."""
    @extend_schema(
        summary="Retrieve a Single Comment",
        description="Fetch a single comment by either a local identifier or a fully qualified identifier (FQID).",
        parameters=[
            OpenApiParameter(
                name="author_serial",
                description="UUID of the author of the post containing the comment.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name="post_serial",
                description="UUID of the post containing the comment.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name="comment_serial",
                description="UUID of the comment itself.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name="comment_fqid",
                description="Fully qualified identifier (FQID) of the comment.",
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH
            )
        ],
        responses={
            200: OpenApiResponse(
                response=CommentSerializer,
                description="Details of the requested comment."
            ),
            400: OpenApiResponse(description="Invalid comment FQID."),
            404: OpenApiResponse(description="Comment not found.")
        }
    )
    def get(self, request, comment_fqid=None, author_serial=None, post_serial=None, comment_serial=None):
        """
        URL: ://service/api/authors/{AUTHOR_SERIAL}/post/{POST_SERIAL}/comment/{REMOTE_COMMENT_FQID}
        http%3A%2F%2Fexample-node-2%2Fauthors%2F5f57808f-0bc9-4b3d-bdd1-bb07c976d12d

        GET [local, remote] a single comment.
        Returns: comment object.
        """
        if comment_serial:
            # Case: Retrieve comment using author, post, and comment serials.
            author = get_object_or_404(User, uuid=author_serial)
            post = get_object_or_404(Post, uuid=post_serial, user=author)

            comment = get_object_or_404(
                Comment, post=post, uuid=comment_serial
            )
        else:
            # Case: Retrieve comment using comment FQID.
            # try:
            #     # TODO splitting and getting the last item is wrong as per the requirements
            #     # we need to make sure that we execute an http request against the fqid since its
            #     # a valid path and since its foreign we shouldn't be trying to retrieve from our database directly
            #     # it all should be done via an http request
            #     comment_id = comment_fqid.split('/')[-1]
            # except IndexError:
            #     return Response(
            #         {"detail": "Invalid comment FQID."}, status=400
            #     )
            try:
                # Validate that comment_fqid is a valid UUID
                comment_id = url_parser.extract_uuid(comment_fqid)
                uuid.UUID(comment_id)  # Raises ValueError if invalid
            except (IndexError, ValueError):
                return Response({"detail": "Invalid comment FQID."}, status=status.HTTP_400_BAD_REQUEST)
            comment = get_object_or_404(Comment, uuid=comment_id)

        # Serialize the comment object.
        serialized_comment = CommentSerializer(comment).data
        return Response(serialized_comment, status=200)
    
    
class CreateCommentView(APIView):
    """
    Handle POST requests to the author's inbox.
    Allows remote or local comments to be added to the post.
    """
    def post(self, request, author_serial):
        # Deserialize the incoming request data
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            post_fqid = serializer.validated_data.get('post')
            post_id = url_parser.extract_uuid(post_fqid) # Extract the post UUID from the FQID
            
            # Fetch the post object using the extracted ID
            post = get_object_or_404(Post, uuid=post_id)

            # Save the comment with the validated data
            serializer.save(post=post)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # If data is invalid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)