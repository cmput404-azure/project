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