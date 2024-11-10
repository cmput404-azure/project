from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import PostSerializer
from django.shortcuts import get_object_or_404
from ..models import Post, User, Follow, Share
from drf_spectacular.utils import extend_schema, OpenApiResponse
import requests
from .posts import PostsPagination

class PublicStreamView(APIView):
    pagination_provider = PostsPagination

    @extend_schema(
        summary="Retrieve Public Posts (and Deleted Posts if Admin)",
        description="Retrieve all public (and deleted) posts available on the node, sorted by the most recent creation date.",
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
        visibility_filter = [1]

        if (request.user and request.user.is_authenticated):
            user = get_object_or_404(User, uuid=request.user.uuid)
            if user.is_staff:
                visibility_filter.append(4) # Add deleted posts for admin

        # Sort the posts by the most recent creation date
        posts = Post.objects.filter(visibility__in=visibility_filter).order_by('-created_at')

        pagination = PostsPagination()

        paginated_posts = pagination.paginate_queryset(posts, request, view=self)

        serialized_posts = PostSerializer(paginated_posts, many=True).data

        return pagination.get_paginated_response(serialized_posts)
    
class AuthStreamView(APIView):
    pagination_provider = PostsPagination

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
            user = get_object_or_404(User, uuid=author_uuid)

            # Query for unlisted and friends-only posts of this user (visibility=2 and visibility=3)
            unlisted_and_friends_posts = Post.objects.filter(
                visibility__in=[2, 3], 
                user=user
            )

            # Retrieve the followees (users the current user is following)
            followee_uuids = Follow.objects.filter(local_follower=user).values_list('local_followee', flat=True) # need to change to account for remote followees in the future

            # Get the actual User objects of the followees based on their UUIDs
            followees = User.objects.filter(uuid__in=followee_uuids)

            print(f"People I'm following: {followees}")

            # Retrieve mutual followers (friends: both following each other)
            # Referenced FollowCustomView for this query
            friends = Follow.objects.filter(
                local_followee=user,
                local_follower__in=followees
            ).values_list('local_follower_id', flat=True)

            print(f"People I'm friends with: {friends}")

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
                  
            pagination = PostsPagination()

            paginated_posts = pagination.paginate_queryset(all_relevant_posts, request, view=self)

            serialized_posts = PostSerializer(paginated_posts, many=True).data

            """
                In this stream, there is also a case where user also see posts shared by people they follow
                All the posts shared are public post as well but it could either remote or local
            """
            # Dictionary to hold unique posts by their post ID or URL (or any unique identifier)
            distinct_shared_posts = {} # can remove distinct if we decided to not have notification for shared post (not required per specification) --> remove receiver in Share model
            
            # Query all shared posts where the user who shared it is in the followees list
            shared_posts = Share.objects.filter(user__in=followees)
            for shared in shared_posts:
                response = requests.get(shared.post) # Post if FQID, we send a request to fetch the Post data
                if response.status_code == 200:
                    shared_data = response.json()
                    shared_data["type"] = "shared" # so we can differentiate in the frontend from normal posts
                    shared_data["shared_by"] = shared.user.display_name
                    unique_key = f"{shared_data.get('id')}_{shared.user.uuid}"
                     
                    # Only add if this exact shared instance (post + sharer) is unique
                    if unique_key not in distinct_shared_posts:
                        distinct_shared_posts[unique_key] = shared_data

            serialized_posts.extend(distinct_shared_posts.values())
            serialized_posts = sorted(serialized_posts, key=lambda x: x.get("published"), reverse=True)

            return pagination.get_paginated_response(serialized_posts)

        else:
            # Return an empty paginated response if not authenticated
            pagination = PostsPagination()
            empty_queryset = Post.objects.none()
            page = pagination.paginate_queryset(empty_queryset, request)
            empty_paginated_response = pagination.get_paginated_response(page if page else [])
            return Response(empty_paginated_response.data, status=status.HTTP_200_OK)
            
