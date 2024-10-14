from rest_framework import serializers
from ..models import Post
from .author import AuthorSerializer
from .comment import CommentSerializer
from .like import LikeSerializer

class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer() 
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