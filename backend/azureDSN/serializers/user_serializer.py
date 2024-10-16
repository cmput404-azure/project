from rest_framework import serializers
from ..models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'host', 'displayName', 'page', 'github', 'profileImage')

    def create(self, validated_data):
        return User.objects.create(**validated_data)
