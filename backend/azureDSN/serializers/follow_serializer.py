from rest_framework import serializers
from .user_serializer import UserSerializer

class FollowSerializer(serializers.ModelSerializer):
    actor = UserSerializer()
    object = UserSerializer()
    class Meta:
        fields = ('summary', 'actor', 'object')
