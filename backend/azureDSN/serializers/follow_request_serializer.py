from rest_framework import serializers
from rest_framework.serializers import *

from ..models import *
from .user_serializer import UserSerializer

class FollowRequestSerializer(serializers.ModelSerializer):
    requester = serializers.JSONField()  
    user_id = SerializerMethodField("get_user_id")  # receiver
    summary = SerializerMethodField("get_summary")
    type = SerializerMethodField("get_type")
    
    class Meta:
        model = FollowRequest
        fields = ("requester", "user_id", "summary", "type")

    def get_user_id(self, obj):
        return UserSerializer(obj.user_id, context=self.context).data

    def get_summary(self, obj):
        requester_name = obj.requester["display_name"]
        return f"{requester_name} wants to follow {obj.user_id.display_name}"

    def get_type(self, obj):
        return "follow"