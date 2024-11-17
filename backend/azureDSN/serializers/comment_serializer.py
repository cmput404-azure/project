from rest_framework import serializers
from rest_framework.serializers import *
from ..models import Comment
from django.conf import settings

class CommentSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(source='uuid')
    published = serializers.DateTimeField(source="created_at", required=False)
    author = serializers.JSONField(source='user')
    post = SerializerMethodField("get_post_FQID")
    
    class Meta:
        model = Comment
        fields = ['type', 'author', 'comment', 'contentType','published','id','post']
    
    # This method gets the custom uuid value and maps it to'id'
    def get_id(self, obj):
        post = obj.post
        return f"{settings.BASE_URL.strip()}/api/authors/{post.user.uuid}/commented/{obj.uuid}"  

    # The returned id field is the value stored in the uuid
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = self.get_id(instance)
        return representation

    # Convert post object into a FQID of post object
    def get_post(self, obj):
        post = str(obj)
        return post.split('/')[-1]
    
    def get_post_FQID(self, obj):
        post = obj.post
        return f"{settings.BASE_URL.strip()}/api/authors/{post.user.uuid}/posts/{post.uuid}"
    '''
    Create new comment object
    '''
    def create(self, validated_data):
        if validated_data.get("published"):
            validated_data["created_at"] = validated_data.pop("published")

        comment_obj = Comment.objects.create(
            **validated_data
        )
        return comment_obj
    
    '''
    Delete a comment
    '''
    def delete(self, comment_obj):
        comment_obj.delete()
        return comment_obj
    
    
    def get_author(self, obj):
        user_data = obj.user  # This should be a dictionary
        return {
            "type": "author",
            "id": user_data.get("id"),  # Ensure this key exists in the JSON
            "host": user_data.get("host"),
            "displayName": user_data.get("displayName"),
            "github": user_data.get("github"),
            "page": user_data.get("page"),
        }
    