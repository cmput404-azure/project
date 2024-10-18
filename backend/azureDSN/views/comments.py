from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from urllib.parse import urlparse

from ..serializers import *
from ..models import *
from ..utils import *

'''
URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments
GET [local, remote]: the comments on the post
'''
class GeneralCommentView(APIView):
    def get(self, request, author_serial, post_serial):
        post = get_object_or_404(Post, id=post_serial, author__id=author_serial)
        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

'''
URL: ://service/api/posts/{POST_FQID}/comments
GET [local, remote]: the comments on the post (that our server knows about)    
'''
class LocalCommentView(APIView):
    def get(self, request, post_fqid):
        post = get_object_or_404(Post, id=post_fqid)
        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


'''
URL: ://service/api/authors/{AUTHOR_SERIAL}/post/{POST_SERIAL}/comment/{REMOTE_COMMENT_FQID}
GET [local, remote] get the comment
'''  
class SingleCommentView(APIView):
    """Handle retrieval of a single comment."""

    def get(self, request, comment_fqid=None, author_serial=None, post_serial=None, comment_serial=None):
        """
        URL: ://service/api/authors/{AUTHOR_SERIAL}/post/{POST_SERIAL}/comment/{REMOTE_COMMENT_FQID}
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
            try:
                comment_id = comment_fqid.split('/')[-1]
            except IndexError:
                return Response(
                    {"detail": "Invalid comment FQID."}, status=400
                )

            comment = get_object_or_404(Comment, uuid=comment_id)

        # Serialize the comment object.
        serialized_comment = CommentSerializer(comment).data
        return Response(serialized_comment, status=200)
    
    

# class SingleLikeView(APIView):
#     """Handle retrieval of a single like."""
#     def get(self, request, like_fqid=None, author_serial=None, like_serial=None):

#         if (like_serial):
#             """
#             URL: ://service/api/authors/{AUTHOR_SERIAL}/liked/{LIKE_SERIAL}
#             GET [local, remote] a single like
#             Returns: like object
#             """
#             print(type(author_serial)) # returns <class 'uuid.UUID'>
#             author = get_object_or_404(User, uuid=author_serial)

#             like = get_object_or_404(Like, user__id = str(author.uuid), uuid=like_serial)
        
#         else:
#             """
#             URL: ://service/api/liked/{LIKE_FQID}
#             GET [local] a single like
#             Returns: like object
#             """
#             # Not yet tested, not sure how to handle FQID yet
#             try:
#                 like_id = like_fqid.split('/')[-1]
#             except IndexError:
#                 return Response(
#                     {"detail": "Invalid like FQID."}, status=400
#                 )
            
#             like = get_object_or_404(Like, uuid=like_id)

#         serialized_like = LikeSerializer(like).data
#         return Response(serialized_like, status=200)