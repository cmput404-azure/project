from rest_framework import serializers
from rest_framework.serializers import *

from ..models import *
from .post_serializer import PostSerializer
from .comment_serializer import CommentSerializer
from .like_serializer import LikeSerializer
from .follow_request_serializer import FollowRequestSerializer


class InboxItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InboxItem
        fields = "__all__"
    
    def to_representation(self, obj):
        if isinstance(obj.content_object, FollowRequest):
            return FollowRequestSerializer(instance=obj.content_obj, context=self.context).data
        elif isinstance(obj.content_object, Post):
            return PostSerializer(instance=obj.content_obj, context=self.context).data
        elif isinstance(obj.content_object, Comment):
            return CommentSerializer(instance=obj.content_obj, context=self.context).data
        elif isinstance(obj.content_object, Like):
            return LikeSerializer(instance=obj.content_obj, context=self.context).data
        elif obj.unused_payload is not None:
            return obj.unused_payload
    
    