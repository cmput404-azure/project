from rest_framework import serializers
from rest_framework.serializers import *

from ..models import *
from serializers import *


class InboxItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InboxItem
        fields = "__all__"
    
    def to_representation(self, obj):
        if isinstance(obj.content_object, Follow):
            # Create Follow obj 
            pass
        elif isinstance(obj.content_object, Post):
            # Create Post obj 
            pass
        elif isinstance(obj.content_object, Comment):
            # Create Comment obj 
            pass
        elif isinstance(obj.content_object, Like):
            # Create Like obj 
            pass
        elif obj.json_data is not None:
            return obj.json_data
    
    