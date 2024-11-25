from django.conf import settings
from ..utils import url_parser
from rest_framework import serializers
from ..models import Like, Post
from django.utils.timezone import make_aware
from drf_spectacular.utils import extend_schema_field

class LikeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(source='user')
    published = serializers.SerializerMethodField(source='created_at')
    id = serializers.SerializerMethodField(source='uuid')
    object = serializers.SerializerMethodField(source='post') # Right now, have not implemented Likes for a Comment object yet

    class Meta:
        model = Like
        fields = ('type', 'author', 'published', 'id', 'object')

    @extend_schema_field(
        {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "id": {"type": "string"},
                "host": {"type": "string"},
                "displayName": {"type": "string"},
                "github": {"type": "string"},
                "page": {"type": "string"},
                "profileImage": {"type": "image"}
            },
        }
    )
    def get_author(self, obj):
        user_data = obj.user  # This should be a dictionary
        return {
            "type": "author",
            "id": f'{user_data.get("id")}',  # Ensure this key exists in the JSON
            "host": user_data.get("host"),
            "displayName": user_data.get("displayName"),
            "github": user_data.get("github"),
            "page": user_data.get("page"),
            "profileImage": user_data.get("profileImage"),
        }
    
    def get_id(self, obj):
        user_data = obj.user
        user_uuid = user_data.get('id', '')
        if (user_uuid):
            user_uuid = user_uuid.rstrip('/').split('/')[-1]
        
        return f"{settings.BASE_URL.strip()}/api/authors/{user_uuid}/liked/{obj.uuid}"
    
    def get_object(self, obj): # currently only works for Post object
        """Construct the FQID for the liked object."""
        post = obj.post
        return f"{settings.BASE_URL.strip()}/api/authors/{post.user.uuid}/posts/{post.uuid}"
    
    def get_published(self, obj):
        dt = obj.created_at
        if not dt.tzinfo:
            dt = make_aware(dt)  # Add timezone info if missing
        return dt.isoformat()

    def create(self, validated_data):
        """Create new Like object"""
        author_data = validated_data.pop('author') # json/dict object

        object_url = validated_data['object'] # the Post object URL
        post_id = url_parser.extract_uuid(object_url)

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
    



    