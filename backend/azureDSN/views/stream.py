from uuid import UUID
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from ..serializers import PostSerializer, InboxItemSerializer
from django.shortcuts import get_object_or_404
from ..models import Post, User, Inbox, InboxItem
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

# TODO if user is admin, also get deleted post

class PublicStreamView(APIView):
    @extend_schema(
        summary="Retrieve Public Posts",
        description="Retrieve all public posts available on the node, sorted by the most recent creation date.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=PostSerializer(many=True),
                description="List of public posts"
            )
        },
    )
    def get(self, request):
        """Retrieve the public posts of the node (currently only working for nodes)"""
        # if author is not authenticated just return the public posts
        public_posts = Post.objects.filter(visibility=1)

        # Sort the posts by the most recent creation date
        public_posts = public_posts.order_by('-created_at')

        # Serialize and return the posts
        serializer = PostSerializer(public_posts, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AuthStreamView(APIView):
    @extend_schema(
        summary="Retrieve Authenticated User's Posts and Inbox",
        description=(
            "Retrieve unlisted and friends-only posts for the authenticated user "
            "and items from the user's inbox related to posts, sorted by publication date."
        ),
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="Combined list of posts and inbox items.",
                response={
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "example": "post"},
                            "title": {"type": "string", "example": "First Post"},
                            "id": {"type": "string", "format": "uuid", "example": "f14c9d67-bc44-4d47-9bda-0fd6f7972b5e"},
                            "contentType": {"type": "string", "example": "text/plain"},
                            "content": {"type": "string", "example": "Hello, world!"},
                            "author": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string", "example": "user-uuid"},
                                    "displayName": {"type": "string", "example": "John Doe"}
                                }
                            },
                            "comments": {"type": "array", "items": {"type": "string"}, "example": []},
                            "likes": {"type": "array", "items": {"type": "string"}, "example": []},
                            "published": {"type": "string", "format": "date-time", "example": "2024-10-21T12:30:00Z"},
                            "visibility": {"type": "integer", "example": 2}
                        },
                    },
                }
            )
        }
    )
    def get(self, request):
        print("Req: ", request)
        print("user: ", request.user)

        if request.user.is_authenticated:
            author_uuid = request.user.uuid
            print(f"the user uuid: {author_uuid}")
            # get author (user) object
            user = get_object_or_404(User, uuid=author_uuid)
            user_inbox = get_object_or_404(Inbox, user=user)

            # Query for unlisted and friends-only posts of this user (visibility=2 and visibility=3)
            unlisted_and_friends_posts = Post.objects.filter(
                visibility__in=[2, 3], 
                user=user
            )
            
            post_content_type = ContentType.objects.get(model="post")
            inbox_items = InboxItem.objects.filter(
                            inbox=user_inbox,
                            content_type=post_content_type,
                            object_id__in=Post.objects.filter(visibility__in=[2, 3]).values_list('uuid', flat=True)
                        ).order_by("-id")
            
            serializer = PostSerializer(unlisted_and_friends_posts, many=True)

            inbox_serializer = InboxItemSerializer(inbox_items, many=True, context={"request": request}) # probably an array

            combined_data = serializer.data + inbox_serializer.data

            combined_data_sorted = sorted(combined_data, key=lambda post: post.get('published'), reverse=True)
            # combined_data_sorted = sorted(combined_data, key=lambda post: post.created_at, reverse=True)

            return Response(combined_data_sorted, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)
            
             

        
