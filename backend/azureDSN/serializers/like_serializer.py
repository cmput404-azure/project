from rest_framework import serializers
from ..models import Like
from  .user_serializer import UserSerializer

class LikeSerializer(serializers.ModelSerializer):
    author = UserSerializer()

    class Meta:
        model = Like
        fields = ('author', 'published', 'id', 'object')