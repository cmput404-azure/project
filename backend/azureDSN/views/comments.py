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
Handle retrieval of all the comments in a post
Both case return a comments object which is a list of comment object
'''
class MultipleCommentsView(APIView):
    def get(self, request, author_serial=None, post_serial=None, post_fqid=None):
        if (author_serial):
            '''
            URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments
            GET [local, remote]: the comments on the post
            '''
            post_id = post_serial
            author_id = author_serial
            post_obj = get_object_or_404(Post, uuid=post_id)
        else:
            '''
            URL: ://service/api/posts/{POST_FQID}/comments
            vd:POST_FQID: http://nodebbbb/api/authors/222/posts/249
            GET [local, remote]: the comments on the post (that our server knows about)    
            '''
            print(post_fqid)
            post_id = post_fqid.split('/')[-1]
            post_obj = get_object_or_404(Post, uuid=post_id)
            author_id = post_obj.user.uuid
            
        comments = Comment.objects.filter(post=post_obj)
        serialized_comments = CommentSerializer(comments, many=True).data
        uri = request.build_absolute_uri("/")
        
        response = {
            "type": "comments",
            "page": f"{uri}api/authors/{author_id}/posts/{post_id}",
            "id": f"{uri}api/authors/{author_id}/posts/{post_id}/comments",
            "page_number": 1,
            "size": 10,
            "count": len(serialized_comments),
            "src": serialized_comments[:10],  # Limit to first 10 comments
        }        
        return Response(response, status.HTTP_200_OK)




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
            try:
                # TODO splitting and getting the last item is wrong as per the requirements
                # we need to make sure that we execute an http request against the fqid since its
                # a valid path and since its foreign we shouldn't be trying to retrieve from our database directly
                # it all should be done via an http request
                comment_id = comment_fqid.split('/')[-1]
            except IndexError:
                return Response(
                    {"detail": "Invalid comment FQID."}, status=400
                )
            comment = get_object_or_404(Comment, uuid=comment_id)

        # Serialize the comment object.
        serialized_comment = CommentSerializer(comment).data
        return Response(serialized_comment, status=200)
    
    
