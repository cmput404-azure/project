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
        local_follower = validated_data.get('local_follower')
        local_followee = validated_data.get('local_followee')

        if local_follower:
            if self.is_valid_uuid(local_follower.uuid):
                print("valid???")

        if local_followee:
            if not self.is_valid_uuid(local_followee.uuid):
                raise serializers.ValidationError({"local_followee": "Invalid UUID for local_followee."})

        return Follow.objects.create(**validated_data)

    
