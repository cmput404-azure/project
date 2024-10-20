from rest_framework import serializers
from ..models import User

class UserSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default='author', read_only=True)
    id = serializers.UUIDField(source='uuid')
    host = serializers.URLField()
    displayName = serializers.CharField(source='display_name')
    github = serializers.URLField()
    profileImage = serializers.ImageField(source='profile_image', use_url=True)
    page = serializers.URLField()

    class Meta:
        model = User
        # TODO: MIGHT NEED TO ADD IMAGE LATER
        fields = ('type', 'id', 'host', 'displayName', 'github', 'page', 'profileImage')

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
        print(data)
        required_fields = ['uuid', 'host', 'display_name', 'github', 'page'] # based on DB schema (image not included right now)
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise serializers.ValidationError(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"}
            )

        return data  # Passed validation