from rest_framework import serializers
from rest_framework.serializers import *
from ..models import Comment, Post

class CommentSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(source='uuid')
    published = serializers.DateTimeField(source="created_at", required=False)
    author = serializers.JSONField()
    post = serializers.CharField()
    
    class Meta:
        model = Comment
        fields = ['type', 'author', 'comment', 'contentType','published','id','post','likes']
    
    # This method gets the custom uuid value and maps it to'id'
    def get_id(self, obj):
        post = obj.post
        return f"{post.user.host}api/authors/{post.user.uuid}/commented/{obj.uuid}"  

    # The returned id field is the value stored in the uuid
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['post_id'] = self.get_id(instance)
        return representation

    # Convert post object into a FQID of post object
    def get_post(self, obj):
        print("!!!!!!!!")
        post = str(obj)
        return post.split('/')[-1]
    
    '''
    Create new comment object
    '''
    def create(self, validated_data):
        print("000000000000")
        print(validated_data)
        if validated_data.get("published"):
            validated_data["created_at"] = validated_data.pop("published")
        user_json = validated_data.pop('author') # json/dict object
        post_id = validated_data["post"].uuid
        post_obj = Post.objects.get(uuid=post_id)

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
            # "profileImage": user_data.get("profileImage"),
        }
    