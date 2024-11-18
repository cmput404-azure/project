
from drf_spectacular.utils import OpenApiExample
from rest_framework import serializers

class NodeSerializer(serializers.Serializer):
    host = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)

    class Meta:
        examples = [
            OpenApiExample(
                name="Node Example",
                value={
                    "host": "http://newnode.com",
                    "username": "newuser",
                    "password": "newpassword123"
                }
            )
        ]
class NodeWithAuthenticationSerializer(NodeSerializer):
    is_authenticated = serializers.BooleanField(default=True)

    class Meta:
        examples = [
            OpenApiExample(
                name="Node Example",
                value={
                    "host": "http://newnode.com",
                    "username": "newuser",
                    "password": "newpassword123",
                    "is_authenticated": True
                }
            )
        ]