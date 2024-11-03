from rest_framework import serializers
from ..models import Share

class ShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share
        fields = [
            'type',
            'receiver',
            'user',
            'post',
            'created_at'
        ]

    def create(self, validated_data):
        return Share.objects.create(**validated_data)
    
    
    
    
    
    
    
