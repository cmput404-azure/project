from rest_framework import serializers
from ..models import Post
from .user_serializer import UserSerializer
from .comment_serializer import CommentSerializer
from .like_serializer import LikeSerializer

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer() 
    comments = CommentSerializer(many=True) 
    likes = LikeSerializer(many=True) 

    class Meta:
        model = Post
        fields = (
            'type',
            'title',
            'id',
            'description',
            'contentType',
            'content',
            'author',
            'comments',
            'likes',
            'published',
            'visibility'
        )