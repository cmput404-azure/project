from rest_framework import serializers
from rest_framework.serializers import *
from ..models import *
from .user_serializer import UserSerializer

class FollowRequestSerializer(serializers.ModelSerializer):
    actor = serializers.JSONField() # requester 
    object = SerializerMethodField("get_user")  # receiver
    summary = SerializerMethodField("get_summary")
    
    class Meta:
        model = FollowRequest
        fields = ["id", "type", "summary", "actor", "object"]

    def get_user(self, obj):
        return UserSerializer(obj.object, context=self.context).data

    def get_summary(self, obj):
        requester_name = obj.actor["displayName"]
        return f"{requester_name} wants to follow {obj.object.display_name}"