from rest_framework import serializers
from .models import Post

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