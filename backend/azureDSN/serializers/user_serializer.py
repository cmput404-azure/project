from rest_framework import serializers
from ..models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        # TODO: need to rename user_id to id in the table
        fields = ['user_id', 'display_name', 'host', 'github', 'profile_image']
        extra_kwargs = {
            'user_id': {'read_only': True}  
        }
