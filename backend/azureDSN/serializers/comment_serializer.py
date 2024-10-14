from rest_framework import serializers
from ..models import Comment
from .user_serializer import UserSerializer

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer()

    class Meta:
        model = Comment
        fields = ('author', 'comment', 'contentType', 'published', 'id', 'post', 'page')
