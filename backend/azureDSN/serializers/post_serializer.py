from rest_framework import serializers
from ..models import Post
from .user_serializer import UserSerializer
from .comment_serializer import CommentSerializer
from .like_serializer import LikeSerializer

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(source='user') 
    # comments = CommentSerializer(many=True) 
    # likes = LikeSerializer(many=True)
    id = serializers.UUIDField(source='uuid')
    contentType = serializers.CharField(source='content_type')
    published = serializers.DateTimeField(source='created_at')
    
    class Meta:
        model = Post
        fields = (
            'type',
            'title',
            'id',
            'contentType',
            'content',
            'author',
            # 'comments',
            # 'likes',
            'published',
            'visibility'
        )

    def create(self, validated_data):
        author_data = validated_data.pop('author')
        author = UserSerializer.create(UserSerializer(), validated_data=author_data)
        post = Post.objects.create(author=author, **validated_data)
        return post
    
    def update(self, post, validated_data):
        author_data = validated_data.pop('author')
        author = UserSerializer.create(UserSerializer(), validated_data=author_data)
        post.author = author
        post.title = validated_data.get('title', post.title)
        post.description = validated_data.get('description', post.description)
        post.contentType = validated_data.get('contentType', post.contentType)
        post.content = validated_data.get('content', post.content)
        post.published = validated_data.get('published', post.published)
        post.visibility = validated_data.get('visibility', post.visibility)
        post.save()
        return post
    
    def delete(self, post):
        post.delete()
        return post