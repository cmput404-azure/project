from rest_framework import serializers
from ..models import Post, User
from .user_serializer import UserSerializer
from rest_framework.response import Response
from django.conf import settings
from urllib.parse import urljoin
import requests, base64


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(source="user")
    comments = serializers.ListField(default=[])
    likes = serializers.ListField(default=[])

    id = serializers.UUIDField(source="uuid", read_only=True)
    contentType = serializers.CharField(source="content_type")
    published = serializers.DateTimeField(source="modified_at")

    class Meta:
        model = Post
        fields = (
            "type",
            "title",
            "id",
            "contentType",
            "content",
            "description",
            "author",
            "comments",
            "likes",
            "published",
            "modified_at",
            "visibility",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        visibility_map = dict(Post.VISIBILITY_CHOICES)
        visibility_value = instance.visibility
        representation["visibility"] = visibility_map[
            visibility_value
        ]  # Need to convert back to string

        # Build the full URL for the id field
        author_uuid = instance.user.uuid
        post_uuid = str(instance.uuid)

        # settings.BASE_URL will always work as long as you have .env file now
        base_url = settings.BASE_URL.strip()
        post_url = f"/api/authors/{author_uuid}/posts/{post_uuid}"
        representation["id"] = urljoin(base_url, post_url)

        # Fetch all likes of the post
        like_url = (
            f"{base_url}/api/authors/{instance.user.uuid}/posts/{instance.uuid}/likes"
        )
        headers = {
            "Internal-Auth": settings.INTERNAL_API_SECRET
        }  # To get through the auth layer

        try:
            response = requests.get(like_url, headers=headers)
            if response.status_code == 200:
                representation["likes"] = response.json()
            else:
                representation["likes"] = {
                    "type": "likes",
                    "page": f"{representation['id']}",
                    "id": f"{representation['id']}/likes",
                    "page_number": 1,
                    "size": 5,
                    "count": 0,
                    "src": [],
                }
        except requests.RequestException as e:
            representation["likes"] = {
                "type": "likes",
                "page": f"{representation['id']}",
                "id": f"{representation['id']}/likes",
                "page_number": 1,
                "size": 5,
                "count": 0,
                "src": [],
            }

        # Fetch all comments of the post
        comment_url = f"{base_url}/api/authors/{instance.user.uuid}/posts/{instance.uuid}/comments"

        try:
            response = requests.get(comment_url, headers=headers)
            if response.status_code == 200:
                representation["comments"] = response.json()
            else:
                representation["comments"] = {
                    "type": "comments",
                    "page": f"{representation['id']}",
                    "id": f"{representation['id']}/comments",
                    "page_number": 1,
                    "size": 5,
                    "count": 0,
                    "src": [],
                }
        except requests.RequestException as e:
            representation["comments"] = {
                "type": "comments",
                "page": f"{representation['id']}",
                "id": f"{representation['id']}/comments",
                "page_number": 1,
                "size": 5,
                "count": 0,
                "src": [],
            }

        return representation

    def create(self, validated_data):
        author_data = validated_data.pop("user")

        if not User.objects.filter(uuid=author_data["uuid"]).exists():
            return Response({"message": "error, unauthorized"}, status=403)

        user = User.objects.get(uuid=author_data["uuid"])

        post = Post.objects.create(user=user, **validated_data)
        return post

    def update(self, post, validated_data):
        author_data = validated_data.pop("author")
        author = UserSerializer.create(UserSerializer(), validated_data=author_data)
        post.author = author
        post.title = validated_data.get("title", post.title)
        post.description = validated_data.get("description", post.description)
        post.contentType = validated_data.get("contentType", post.contentType)
        post.content = validated_data.get("content", post.content)
        post.published = validated_data.get("published", post.modified_at)
        post.modified_at = validated_data.get("modified_at", post.modified_at)
        post.visibility = validated_data.get("visibility", post.visibility)
        post.save()
        return post

    def delete(self, post):
        post.delete()
        return post


class CreatePostSerializer(serializers.ModelSerializer):
    author = UserSerializer(source="user")
    id = serializers.UUIDField(source="uuid", read_only=True)
    contentType = serializers.CharField(source="content_type")
    published = serializers.DateTimeField(source="created_at")
    description = serializers.CharField(
        required=False, allow_blank=True
    )  # can be empty on post creation
    content = serializers.CharField(
        required=True, allow_blank=False
    )  # must contain content (which is a base64 encoded image or normal text)
    github_id = serializers.CharField(required=False, allow_null=True)
    visibility = serializers.ChoiceField(choices=Post.VISIBILITY_CHOICES, default=1)

    class Meta:
        model = Post
        fields = (
            "type",
            "title",
            "id",
            "contentType",
            "content",
            "description",
            "author",
            "published",
            "visibility",
            "github_id",
        )

    def create(self, validated_data):
        author_data = validated_data.pop("user")

        if not User.objects.filter(uuid=author_data["uuid"]).exists():
            return Response({"message": "error, unauthorized"}, status=403)

        user = User.objects.get(uuid=author_data["uuid"])

        content_type = validated_data.get("content_type")

        if content_type in [
            "image/png;base64",
            "image/jpeg;base64",
            "application/base64",
        ]:
            try:
                content = validated_data.get("content")
                base64.b64decode(content)
                validated_data["has_image"] = True
            except (ValueError, TypeError):
                raise serializers.ValidationError("Cannot be dencoded into base64.")
            validated_data["has_image"] = True
        else:
            validated_data["has_image"] = False

        # Check github id to prevent duplicates
        github_id = validated_data.get("github_id")
        if github_id:
            if Post.objects.filter(github_id=github_id).exists():
                raise serializers.ValidationError("GitHub ID already retrieved.")

        post = Post.objects.create(user=user, **validated_data)
        return post

    # Convert the integer visibility back to string when serializing the response
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # build fqid for post
        author_uuid = instance.user.uuid
        post_uuid = str(instance.uuid)

        visibility_str = dict(Post.VISIBILITY_CHOICES).get(instance.visibility)
        representation["visibility"] = visibility_str

        # settings.BASE_URL will always work as long as you have .env file now
        base_url = settings.BASE_URL.strip()
        post_url = f"/api/authors/{author_uuid}/posts/{post_uuid}"
        representation["id"] = urljoin(base_url, post_url)

        # Empty pagination objects on creation, without calling Likes and Comments API
        representation["likes"] = {
            "type": "likes",
            "page": f"{representation['id']}",
            "id": f"{representation['id']}/likes",
            "page_number": 1,
            "size": 5,
            "count": 0,
            "src": [],
        }

        representation["comments"] = {
            "type": "comments",
            "page": f"{representation['id']}",
            "id": f"{representation['id']}/comments",
            "page_number": 1,
            "size": 5,
            "count": 0,
            "src": [],
        }

        return representation
