from rest_framework import serializers
from rest_framework.serializers import *

from ..models import *

class InboxItemSerializer(serializers.ModelSerializer):
    class Meta:
        # model = InboxItem
        fields = "__all__"

    def to_representation(self, obj):
        if isinstance(obj.content_object, Follow):
            pass
        elif isinstance(obj.content_object, Post):
            pass
        elif isinstance(obj.content_object, Comment):
            pass
        elif isinstance(obj.content_object, Like):
            pass
        elif obj.json_data is not None:
            return obj.json_data