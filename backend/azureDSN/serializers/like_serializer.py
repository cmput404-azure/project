
from .post_serializer import PostSerializer
from rest_framework import serializers
from ..models import Like, Post
from .user_serializer import UserSerializer


class LikeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(source='user')
    published = serializers.DateTimeField(source='created_at')
    id = serializers.UUIDField(source='uuid')
    object = PostSerializer(source='post')

    class Meta:
        model = Like
        fields = ('type', 'author', 'published', 'id', 'object')

    def get_author(self, obj):
        user_data = obj.user  # This should be a dictionary
        return {
            "type": "author",
            "id": user_data.get("id"),  # Ensure this key exists in the JSON
            "host": user_data.get("host"),
            "displayName": user_data.get("displayName"),
            "github": user_data.get("github"),
            # "profileImage": user_data.get("profileImage"),
        }

    def create(self, validated_data):
        """Create new Like object"""
        author_data = validated_data.pop('author') # json/dict object

        object_url = validated_data['object'] # the Post object URL
        post_id = object_url.split('/')[-1] # Post 'id' is always the last part of the URL

        post = Post.objects.get(id=post_id)
        like = Like.objects.create(
            user=author_data,
            post_id=post,
            **validated_data
        )

        return like

    def delete(self, like):
        like.delete()
        return like
    
# class LikesSerializer(serializers.Serializer):
#     type = serializers.CharField(default='likes')
#     id = serializers.URLField()
#     page = serializers.URLField()
#     page_number = serializers.IntegerField(default=1)
#     size = serializers.IntegerField(default=50)
#     count = serializers.IntegerField()
#     src = LikeSerializer(many=True)


    