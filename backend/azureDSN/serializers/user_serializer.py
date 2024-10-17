from rest_framework import serializers
from ..models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('uuid', 'host', 'display_name', 'page', 'github', 'profile_image', 'created_at', 'modified_at')

    def create(self, validated_data):
        return User.objects.create(**validated_data)
