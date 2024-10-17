from rest_framework import serializers
from ..models import User

class UserSerializer(serializers.ModelSerializer):
    type = serializers.CharField(read_only=True)
    id = serializers.UUIDField(source='uuid')
    host = serializers.URLField()
    displayName = serializers.CharField(source='display_name')
    github = serializers.URLField()
    profileImage = serializers.ImageField(source='profile_image')
    page = serializers.URLField()

    class Meta:
        model = User
        fields = ('type', 'id', 'host', 'displayName', 'github', 'profileImage', 'page')

    def create(self, validated_data):
        return User.objects.create(**validated_data)
