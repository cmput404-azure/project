from rest_framework import serializers
from ..models import Follow

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = [
            'local_follower',
            'remote_follower',
            'local_followee',
            'remote_followee',
            'created_at',
        ]

    def create(self, validated_data):
        return Follow.objects.create(**validated_data)
