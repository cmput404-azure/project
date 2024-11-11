from rest_framework import serializers
from rest_framework.serializers import *
from ..models import *
from .post_serializer import PostSerializer
from .comment_serializer import CommentSerializer
from .like_serializer import LikeSerializer
from .follow_request_serializer import FollowRequestSerializer
from .share_serializer import ShareSerializer

class InboxItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InboxItem
        fields = "__all__"
    
    # Reference on how to achive polymorphic pattern in Django with serializer - Syas Jun 23, 2017
    # https://stackoverflow.com/questions/19976202/django-rest-framework-django-polymorphic-modelserialization
    def to_representation(self, obj):
        if isinstance(obj.content_object, FollowRequest):
            return FollowRequestSerializer(instance=obj.content_object, context=self.context).data
        elif isinstance(obj.content_object, Post):
            post_data = PostSerializer(instance=obj.content_object, context=self.context).data
            if obj.post_status is not None:
                post_data['post_status'] = obj.post_status # this is to help add status for updated and deleted post
            return post_data
        elif isinstance(obj.content_object, Comment):
            return CommentSerializer(instance=obj.content_object, context=self.context).data
        elif isinstance(obj.content_object, Like):
            return LikeSerializer(instance=obj.content_object, context=self.context).data
        elif isinstance(obj.content_object, Share):
            return ShareSerializer(instance=obj.content_object, context=self.context).data
        elif obj.remote_payload is not None:
            result = obj.remote_payload
            if obj.post_status is not None:
                result['post_status'] = obj.post_status
            return result
 