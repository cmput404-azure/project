from rest_framework import serializers
from ..models import User
from django.conf import settings
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from rest_framework import serializers

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Single Author Example",
            value={
                "type": "author",
                "id": "http://nodeaaaa/api/authors/111",
                "host": "http://nodeaaaa/api/",
                "displayName": "Greg Johnson",
                "github": "http://github.com/gjohnson",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "page": "http://nodeaaaa/authors/greg"
            }
        ),
        OpenApiExample(
            "All Authors Example",
            value={
                "type": "authors",
                "authors": [
                    {
                        "type": "author",
                        "id": "http://nodeaaaa/api/authors/111",
                        "host": "http://nodeaaaa/api/",
                        "displayName": "Greg Johnson",
                        "github": "http://github.com/gjohnson",
                        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                        "page": "http://nodeaaaa/authors/greg"
                    },
                    {
                        "type": "author",
                        "id": "http://nodeaaaa/api/authors/222",
                        "host": "http://nodeaaaa/api/",
                        "displayName": "Jane Smith",
                        "github": "http://github.com/jsmith",
                        "profileImage": "https://i.imgur.com/n8pLKBs.jpeg",
                        "page": "http://nodeaaaa/authors/jane"
                    }
                ]
            }
        )
    ]
)
class UserSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default='author', read_only=True)
    id = serializers.UUIDField(source='uuid')
    host = serializers.URLField()
    displayName = serializers.CharField(source='display_name')
    username = serializers.CharField()
    bio = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    github = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    page = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    profileImage = serializers.CharField(required=False, allow_null=True, allow_blank=True, source='profile_image')

    class Meta:
        model = User
        fields = ('type', 'id', 'host', 'displayName', 'username', 'bio', 'github', 'page', 'profileImage')
    
    # This method gets the custom uuid value and maps it to'id'
    def get_id(self, obj):
        return f"{obj.host}authors/{obj.uuid}"

    # The returned id field is the value stored in the uuid
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = self.get_id(instance)
        return representation

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Custom update logic to map JSON keys to DB fields.
        """
        for attr, value in validated_data.items():
            if attr == 'displayName':
                setattr(instance, 'display_name', value)
            elif attr == 'profileImage':
                setattr(instance, 'profile_image', value)
            else:
                setattr(instance, attr, value) # JSON keys have the same name as DB field

        instance.save()
        return instance
    
    def validate(self, data):
        """
        Check if the payload have the expected fields.
        """
        required_fields = ['uuid', 'host', 'display_name', 'github', 'page'] # based on DB schema (image not included right now)
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise serializers.ValidationError(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"}
            )

        return data  # Passed validation