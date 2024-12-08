from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.shortcuts import get_object_or_404
from ..serializers import PostSerializer
from ..models import Post, User, Follow, Share, Inbox
from ..utils import url_parser
from .posts import PostsPagination
from requests.auth import HTTPBasicAuth
import requests, os

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
        """Retrieve the public posts of the node and remote posts in the user's inbox."""

        # Default visibility filter for public posts
        visibility_filter = [1]

        # If the user is authenticated, customize the visibility filter
        if request.user and request.user.is_authenticated:
            user = get_object_or_404(User, uuid=request.user.uuid)
            if user.is_staff:
                visibility_filter.append(4)  # Add deleted posts for admin

        remote_posts = {}
        processed_posts = {}  # A dictionary to track post_id and post_status
        for inbox in Inbox.objects.all(): # Iterate through all local inboxes
            for item in inbox.items.filter(remote_payload__isnull=False):
                remote_payload = item.remote_payload
                if remote_payload.get("type") == "post": # And get the remote posts
                    post_id = remote_payload.get("id")
                    visibility = remote_payload.get("visibility").upper()

                    if (visibility == "DELETED"):
                        # We don't want to see deleted remote posts
                        if post_id in remote_posts:
                            remote_posts.pop(post_id) # Remove deleted post
                    
                    if item.post_status != None and item.post_status in ["edited", "update-old"]:
                            # don't handle old post
                            continue

                    if visibility == "PUBLIC" and (item.post_status == None or item.post_status.upper() != "DELETE"): # This logic only works for local, local-remote posts
                        if post_id in processed_posts and processed_posts[post_id] == item.post_status:
                            # Skip if the post has already been processed with the same status
                            # This should work for remote-remote edited posts? Because we are fetching post from their endpoint directly (it will show latest content)
                            continue
                        
                        if visibility == "UNLISTED" or visibility == "FRIENDS":
                            continue

                        author_host = remote_payload["author"]["host"]
                        base_author_host = url_parser.get_base_host(author_host)
                        post_uuid = url_parser.extract_uuid(post_id)
                        author_fqid = remote_payload["author"]["id"]
                        author_uuid = url_parser.extract_uuid(author_fqid)

                        get_post_url = f"{base_author_host}/api/authors/{author_uuid}/posts/{post_uuid}"
                        try:
                            # Perform the GET request
                            response = requests.get(
                                get_post_url,
                                auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD'))
                            )

                            if response.status_code == 200:
                                post_data = response.json()

                                if post_id not in remote_posts: # Add if this post hasn't been added
                                    remote_posts[post_id] = post_data
                                elif item.post_status and item.post_status.upper() == "UPDATE":
                                    # There's a newer version of this post
                                    remote_posts[post_id] = post_data

                            else: # Remote node doesn't give authorization
                                print(f"Failed to fetch post. Status code: {response.status_code}")

                            processed_posts[post_id] = item.post_status # Regardless of whether fail or success

                        except Exception as e:
                            print(f"Error fetching remote post {get_post_url}: {e}")

        unique_remote_posts = list(remote_posts.values())

        local_posts = Post.objects.filter(visibility__in=visibility_filter)

        serialized_local_posts = PostSerializer(local_posts, many=True).data

        all_posts = serialized_local_posts + unique_remote_posts

        # Separate logic for Post objects and JSON objects
        all_posts.sort(key=lambda post: post['published'] if isinstance(post, dict) else post['modified_at'], reverse=True)

        pagination = PostsPagination()
        paginated_posts = pagination.paginate_queryset(all_posts, request, view=self)

        return pagination.get_paginated_response(paginated_posts)
    
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
        if request.user.is_authenticated:
            author_uuid = request.user.uuid
            user = get_object_or_404(User, uuid=author_uuid)

            # Query for friends-only and unlisted posts authored by this user
            unlisted_and_friends_posts = Post.objects.filter(
                visibility__in=[2, 3], 
                user=user
            )

            # Retrieve the local followees (users the current user is following)
            followee_uuids = Follow.objects.filter(local_follower=user).values_list('local_followee', flat=True)

            # Get the actual User objects of the followees based on their UUIDs
            local_followees = User.objects.filter(uuid__in=followee_uuids)

            # Retrieve mutual followers (friends: both following each other)
            friends = Follow.objects.filter(
                local_followee=user,
                local_follower__in=local_followees
            ).values_list('local_follower_id', flat=True)

            # Query for local followees' unlisted posts
            followees_unlisted_posts = Post.objects.filter(
                user__in=local_followees,
                visibility=3
            )

            # Query for local friends' friends-only posts
            friends_only_posts = Post.objects.filter(
                user__in=friends,
                visibility=2
            )

            all_relevant_local_posts = unlisted_and_friends_posts | followees_unlisted_posts | friends_only_posts

            # Remove local duplicates and sort by creation date
            all_relevant_local_posts = all_relevant_local_posts.order_by("-created_at").distinct()
                  
            pagination = PostsPagination()

            paginated_posts = pagination.paginate_queryset(all_relevant_local_posts, request, view=self)

            serialized_local_posts = PostSerializer(paginated_posts, many=True).data

            # Handle remote posts from the user's inbox
            remote_posts = {}
            processed_posts = {}
            user_inbox = Inbox.objects.filter(user=user)

            for inbox in user_inbox:
                for item in inbox.items.filter(remote_payload__isnull=False):
                    remote_payload = item.remote_payload
                    if remote_payload.get("type") == "post":
                        visibility = remote_payload.get("visibility", "").upper()
                        if visibility not in ["FRIENDS", "UNLISTED"]:
                            continue
                        
                        if item.post_status != None and item.post_status in ["edited", "update-old"]:
                            # don't handle old post
                            continue

                        post_id = remote_payload.get("id")
                        if post_id in processed_posts and processed_posts[post_id] == item.post_status:
                            # Skip already processed posts with the same status
                            continue
                        

                        base_host = url_parser.get_base_host(remote_payload.get("id"))
                        author_serial = url_parser.extract_uuid(remote_payload.get("author").get("id"))
                        post_serial = url_parser.extract_uuid(remote_payload.get("id"))
                        get_post_url = f"{base_host}/api/authors/{author_serial}/posts/{post_serial}"

                        try:
                            response = requests.get(
                                get_post_url,
                                auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD'))
                            )

                            if response.status_code == 200:
                                post_data = response.json()

                                if post_id not in remote_posts: # Add if this post hasn't been added
                                    remote_posts[post_id] = post_data
                                elif item.post_status and item.post_status.upper() == "UPDATE":
                                    # There's a newer version of this post
                                    remote_posts[post_id] = post_data

                            elif response.status_code == 500: # Whitesmoke post endpoint
                                if visibility == "FRIENDS":
                                    author_serial = url_parser.extract_uuid(remote_payload.get("author").get("id"))
                                    post_serial = url_parser.extract_uuid(remote_payload.get("id"))

                                    try:
                                        # Fetch friends-only likes
                                        response = requests.get(
                                            f"{base_host}/api/authors/{author_serial}/posts/{post_serial}/likes",
                                            auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD'))
                                        )

                                        if response.status_code == 200:
                                            remote_payload['likes'] = response.json()

                                            # Fetch friends-only comments
                                            response = requests.get(
                                                f"{base_host}/api/authors/{author_serial}/posts/{post_serial}/comments",
                                                auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD'))
                                            )

                                            if response.status_code == 200:
                                                remote_payload['comments'] = response.json()

                                        else:
                                            print(f"Unable to fetch remote post with ID (Inside elif): {post_id}")

                                    except Exception as e:
                                        print(f"Error fetching likes and comments {post_id}: {e}")

                                    print(f"This should contain latest likes and comments: {remote_payload}")
                                    if post_id not in remote_posts: # Add if this post hasn't been added
                                        remote_posts[post_id] = remote_payload
                                    elif item.post_status and item.post_status.upper() == "UPDATE":
                                        # There's a newer version of this post
                                        remote_posts[post_id] = remote_payload

                            else:
                                print(f"Unable to fetch remote post with ID (Inside else): {post_id}")
                
                            processed_posts[post_id] = item.post_status

                        except Exception as e:
                            print(f"Error fetching post {post_id}: {e}")

            combined_posts = serialized_local_posts.copy()
            
            for post_id, post_data in remote_posts.items():
                combined_posts.append(post_data)

            """
                In this stream, there is also a case where user also see posts shared by people they follow
                All the posts shared are public post as well but it could either remote or local
            """
            # Dictionary to hold unique posts by their post ID or URL (or any unique identifier)
            distinct_shared_posts = {} # can remove distinct if we decided to not have notification for shared post (not required per specification) --> remove receiver in Share model
            
            # Query all shared posts where the user who shared it is in the followees list
            shared_posts = Share.objects.filter(user__in=local_followees)
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

            combined_posts.extend(distinct_shared_posts.values())
            combined_posts = sorted(combined_posts, key=lambda x: x.get("published"), reverse=True)

            return pagination.get_paginated_response(combined_posts)

        else:
            # Return an empty paginated response if not authenticated
            pagination = PostsPagination()
            empty_queryset = Post.objects.none()
            page = pagination.paginate_queryset(empty_queryset, request)
            empty_paginated_response = pagination.get_paginated_response(page if page else [])
            return Response(empty_paginated_response.data, status=status.HTTP_200_OK)
            
