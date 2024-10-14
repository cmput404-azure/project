from rest_framework import serializers
from ..models import Like
from .author import AuthorSerializer

class LikeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Like
        fields = ('author', 'published', 'id', 'object')