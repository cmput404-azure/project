from uuid import UUID
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from ..serializers import PostSerializer, InboxItemSerializer
from django.shortcuts import get_object_or_404
from ..models import Post, User, Inbox, InboxItem, Follow, Share
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import requests

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

            # Query for unlisted and friends-only posts of this user (visibility=2 and visibility=3)
            unlisted_and_friends_posts = Post.objects.filter(
                visibility__in=[2, 3], 
                user=user
            )

            # Retrieve the followees (users the current user is following)
            followees = Follow.objects.filter(local_follower=user).values_list('local_followee', flat=True)

            # Retrieve mutual followers (friends: both following each other)
            # Referenced FollowCustomView for this query
            friends = Follow.objects.filter(
                local_followee=user,
                local_follower_id__in=followees
            ).values_list('local_follower_id', flat=True)

            # Query for followees' unlisted posts
            followees_unlisted_posts = Post.objects.filter(
                user__in=followees,
                visibility=3
            )

            # Query for friends' friends-only posts
            friends_only_posts = Post.objects.filter(
                user__in=friends,
                visibility=2
            )

            all_relevant_posts = unlisted_and_friends_posts | followees_unlisted_posts | friends_only_posts

            # Remove duplicates and sort by creation date
            all_relevant_posts = all_relevant_posts.order_by("-created_at").distinct()
            combined_data = PostSerializer(all_relevant_posts, many=True).data
            
                
            """
            In this stream, there is also a case where user also see posts shared by people they follow
            All the posts shared are public post as well but it could either remote or local
            """
            # Query all items in the Share table whose receiver is the same as current user
            shared_posts = Share.objects.filter(receiver = user)
            for shared in shared_posts:
                # here the post is the fqid
                # we send a request to fetch the post data
                response = requests.get(shared.post)
                if response.status_code == 200:
                    shared_data = response.json()
                    combined_data.append(shared_data)

            return Response(combined_data, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)
            
             

        
