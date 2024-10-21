from uuid import UUID
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from ..serializers import PostSerializer, InboxItemSerializer
from django.shortcuts import get_object_or_404
from ..models import Post, User, Inbox, InboxItem, Follow
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

            # Retrieve the followees (users the current user is following)
            followees = Follow.objects.filter(local_follower=user).values_list('local_followee', flat=True)

            # Retrieve the mutual followers (friends: both following each other)
            friends = Follow.objects.filter(
                Q(local_follower=user, local_followee__in=followees) |
                Q(local_followee=user, local_follower__in=followees)
            ).values_list('local_followee', flat=True)

            followees_set = set(followees)
            friends_set = set(friends)

            relevant_posts = Post.objects.filter(
                Q(user__in=friends_set, visibility=3) |  # Friends-only posts
                Q(user__in=followees_set, visibility=2)  # Followees' posts
            ).order_by("-created_at")

            # Serialize both datasets
            unlisted_and_friends_serializer = PostSerializer(unlisted_and_friends_posts, many=True)
            relevant_serializer = PostSerializer(relevant_posts, many=True)

            # Combine serialized data without duplicates (using unique post UUIDs)
            combined_data = {post['id']: post for post in (unlisted_and_friends_serializer.data + relevant_serializer.data)}
            combined_data_list = list(combined_data.values())  # Convert back to list

            print(combined_data)

            combined_data_sorted = sorted(combined_data_list, key=lambda post: post.get('published'), reverse=True)
            # combined_data_sorted = sorted(combined_data, key=lambda post: post.created_at, reverse=True)

            return Response(combined_data_sorted, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)
            
             

        
