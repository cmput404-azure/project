from rest_framework import serializers
from ..models import Post, User, Like
from .user_serializer import UserSerializer
from .comment_serializer import CommentSerializer
from .like_serializer import LikeSerializer
from rest_framework.response import Response
import base64
from django.conf import settings
from urllib.parse import urljoin
from ..views.likes import LikesView
from rest_framework.test import APIRequestFactory

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(source='user') 
    # comments = CommentSerializer(many=True) 
    # likes = LikeSerializer(many=True)
    comments = serializers.ListField(default=[])
    likes = serializers.ListField(default=[])
    
    id = serializers.UUIDField(source='uuid', read_only=True)
    contentType = serializers.CharField(source='content_type')
    published = serializers.DateTimeField(source='created_at')

    # content = serializers.CharField(required=True, allow_blank=False) # must contain content (which is a base64 encoded image or normal text)
    
    class Meta:
        model = Post
        fields = (
            'type',
            'title',
            'id',
            'contentType',
            'content',
            'description',
            'author',
            'comments',
            'likes',
            'published',
            'visibility',
        )
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Build the full URL for the id field
        author_uuid = instance.user.uuid
        post_uuid = str(instance.uuid)
        base_url = settings.BASE_URL
        post_url = f'/api/authors/{author_uuid}/posts/{post_uuid}'
        representation['id'] = urljoin(base_url, post_url)
        
        # Create an internal request to the LikesView with the required params
        likeFactory = APIRequestFactory()
        likeRequest = likeFactory.get(f'/api/authors/{instance.user.uuid}/posts/{instance.uuid}/likes')
        likeView = LikesView.as_view()
        
        # Call LikesView and capture the response
        response = likeView(likeRequest, author_serial=instance.user.uuid, post_serial=instance.uuid)

        # Ensure the response is successful and set likes data
        if response.status_code == 200:
            representation['likes'] = response.data
        else:
            representation['likes'] = []
        
        return representation
    
    def create(self, validated_data):
        author_data = validated_data.pop('user')

        if not User.objects.filter(uuid=author_data['uuid']).exists():
            return Response({"message": "error, unauthorized"},status=403)
        
        user = User.objects.get(uuid=author_data['uuid'])

        # content_type = validated_data.get('content_type')

        # if content_type in ['image/png;base64', 'image/jpeg;base64', 'application/base64']:
        #     try:
        #         image = validated_data['content']
        #         base64.b64encode(image)
        #     except (ValueError, TypeError):
        #         raise serializers.ValidationError("Cannot be encoded into base64.")
        #     validated_data['has_image'] = True
        # else:
        #     validated_data['has_image'] = False

        post = Post.objects.create(user=user, **validated_data)
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
    

class CreatePostSerializer(serializers.ModelSerializer):
    author = UserSerializer(source='user') 
    id = serializers.UUIDField(source='uuid', read_only=True)
    contentType = serializers.CharField(source='content_type')
    published = serializers.DateTimeField(source='created_at')
    description = serializers.CharField(required=False)
    content = serializers.CharField(required=True, allow_blank=False)  # Must contain content (text or base64 image)
    github_id = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = (
            'type',
            'title',
            'id',
            'contentType',
            'content',
            'description',
            'author',
            'published',
            'visibility',
            'github_id',
        )

    def create(self, validated_data):
        author_data = validated_data.pop('user')

        if not User.objects.filter(uuid=author_data['uuid']).exists():
            raise serializers.ValidationError("Error, unauthorized.")

        user = User.objects.get(uuid=author_data['uuid'])
        
        content_type = validated_data.get('content_type')
        if content_type in ['image/png;base64', 'image/jpeg;base64', 'application/base64']:
            try:
                content = validated_data.get('content')
                base64.b64decode(content)
                validated_data['has_image'] = True
            except (ValueError, TypeError):
                raise serializers.ValidationError("Content cannot be decoded from base64.")
            validated_data['has_image'] = True
        else:
            validated_data['has_image'] = False

        # Check GitHub ID to prevent duplicates
        github_id = validated_data.get('github_id')
        if github_id:
            if Post.objects.filter(github_id=github_id).exists():
                raise serializers.ValidationError("This GitHub activity has already been retrieved.")
        
        post = Post.objects.create(user=user, **validated_data)
        return post