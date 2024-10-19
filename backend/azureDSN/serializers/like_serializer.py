
from .post_serializer import PostSerializer
from rest_framework import serializers
from ..models import Like, Post
from .user_serializer import UserSerializer
from django.utils.timezone import make_aware

class LikeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(source='user')
    published = serializers.SerializerMethodField(source='created_at')
    id = serializers.SerializerMethodField(source='uuid')
    object = serializers.SerializerMethodField(source='post') # Right now, have not implemented Likes for a Comment object yet

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
            "page": user_data.get("page"),
            # "profileImage": user_data.get("profileImage"),
        }
    
    def get_id(self, obj):
        user_data = obj.user

        # host = user_data.get('host', '')
        user_uuid = user_data.get('id', '')

        # return f"{host}api/authors/{user_uuid}/liked/{obj.uuid}"
        return f"api/authors/{user_uuid}/liked/{obj.uuid}"
    
    def get_object(self, obj): # currently only works for Post object
        """Construct the FQID for the liked object."""
        post = obj.post
        # return f"{post.user.host}api/authors/{post.user.uuid}/posts/{post.uuid}"
        return f"api/authors/{post.user.uuid}/posts/{post.uuid}"
    
    def get_published(self, obj):
        dt = obj.created_at
        if not dt.tzinfo:
            dt = make_aware(dt)  # Add timezone info if missing
        return dt.isoformat()

    def create(self, validated_data):
        """Create new Like object"""
        author_data = validated_data.pop('author') # json/dict object

        object_url = validated_data['object'] # the Post object URL
        post_id = object_url.split('/')[-1] # Post 'id' is always the last part of the URL

        post = Post.objects.get(uuid=post_id)
        like = Like.objects.create(
            user=author_data,
            post=post,
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


    