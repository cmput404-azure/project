from rest_framework import serializers
from ..models import Comment
from .author import AuthorSerializer

class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Comment
        fields = ('author', 'comment', 'contentType', 'published', 'id', 'post', 'page')
