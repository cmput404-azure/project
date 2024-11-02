import uuid
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from ..serializers import *
from ..models import *
from ..utils import *

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
    def get(self, request, author_serial=None, post_serial=None, post_fqid=None):
        if (author_serial):
            '''
            URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments
            GET [local, remote]: the comments on the post
            '''
            post_id = post_serial
            post_obj = get_object_or_404(Post, uuid=post_serial, user__uuid=author_serial)
        else:
            '''
            URL: ://service/api/posts/{POST_FQID}/comments
            vd:POST_FQID: http://nodebbbb/api/authors/222/posts/249
            GET [local, remote]: the comments on the post (that our server knows about)    
            '''
            post_id = post_fqid.split('/')[-1]

            # Validate if `post_id` is a valid UUID
            try:
                uuid.UUID(post_id)
            except ValueError:
                return Response({"detail": "Invalid post FQID."}, status=status.HTTP_400_BAD_REQUEST)

            post_obj = get_object_or_404(Post, uuid=post_id)

        comments = Comment.objects.filter(post=post_obj)

        pagination = self.pagination_provider()
        page = pagination.paginate_queryset(comments, request)

        serialized_comments = CommentSerializer(page, many=True).data
        return pagination.get_paginated_response(serialized_comments)

'''
URL: ://service/api/authors/{AUTHOR_SERIAL}/post/{POST_SERIAL}/comment/{REMOTE_COMMENT_FQID}
GET [local, remote] get the comment
'''  
class SingleCommentView(APIView):
    """Handle retrieval of a single comment."""

    def get(self, request, comment_fqid=None, author_serial=None, post_serial=None, comment_serial=None):
        """
        URL: ://service/api/authors/{AUTHOR_SERIAL}/post/{POST_SERIAL}/comment/{REMOTE_COMMENT_FQID}
        http%3A%2F%2Fexample-node-2%2Fauthors%2F5f57808f-0bc9-4b3d-bdd1-bb07c976d12d

        GET [local, remote] a single comment.
        Returns: comment object.
        """
        if comment_serial:
            # Case: Retrieve comment using author, post, and comment serials.
            print(type(author_serial))  # returns <class 'uuid.UUID'>
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
                comment_id = comment_fqid.split('/')[-1]
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
        print("@@@@@@@")
        print(request.data)
        if serializer.is_valid():
            print("#######")
            print(serializer.validated_data)
            post_fqid = serializer.validated_data.get('post')
            post_id = post_fqid.split('/')[-1]  # Extract the post UUID from the FQID
            
            # Fetch the post object using the extracted ID
            post = get_object_or_404(Post, uuid=post_id)

            # Save the comment with the validated data
            serializer.save(post=post)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # If data is invalid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)