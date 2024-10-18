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
    def get(self, request, author_serial, post_serial, remote_comment_fqid):
        comment = get_object_or_404(Comment, id=remote_comment_fqid, post__id=post_serial, post__author__id=author_serial)
        serializer = CommentSerializer(comment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
'''
URL: ://service/api/comment/{COMMENT_FQID}
GET [local] get the comment
'''    
class AllCommentView(APIView):
    def get(self, request, comment_fqid):
        comment = get_object_or_404(Comment, id=comment_fqid)
        serializer = CommentSerializer(comment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)