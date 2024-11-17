from urllib.parse import unquote, urlparse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from ..models import User, Post, Follow
from ..serializers import PostSerializer, UserSerializer, CreatePostSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework.pagination import PageNumberPagination
from uuid import UUID
from django.conf import settings
import requests

class AuthorPostView(APIView):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}
    URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/
    """
    
    @extend_schema(
        summary="Retrieve a Post",
        description="Retrieve a specific Post object by `post_serial` or a combination of `author_serial` and `post_serial`. Returns a 404 if not found.",
        parameters=[
            OpenApiParameter(
                name='author_serial',
                description='UUID of the Author of the Post to retrieve',
                type=str,
                required=True,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name='post_serial',
                description='UUID of the Post to retrieve',
                type=str,
                required=False,
                location=OpenApiParameter.PATH
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=PostSerializer, description='Post retrieved successfully'),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Post or Author not found.'),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Invalid Post Serial or Author Serial'),
        },
        tags=['Posts API']
    )
    def get(self, request, author_serial, post_serial):
        """
        GET [local, remote] get the public post whose serial is POST_SERIAL
            - friends-only posts: must be authenticated
            
        GET [local, remote] get the recent posts from author AUTHOR_SERIAL (paginated)
            - Not authenticated: only public posts.
            - Authenticated locally as author: all posts.
            - Authenticated locally as friend of author: public + friends-only posts.
            - Authenticated as remote node: This probably should not happen. Remember, the way remote node becomes aware of local posts is by local node pushing those posts to inbox, not by remote node pulling.
        """
        if not User.objects.filter(uuid=author_serial).exists(): 
            return Response("Author does not exist.", status=404)

        if (author_serial and post_serial):
            author = get_object_or_404(User, uuid=author_serial)
            post = get_object_or_404(Post, uuid=post_serial, user=author)

            # Check visibility for permission logic:
            if post.visibility == 1:  # PUBLIC
                # Public posts are visible to everyone
                serializer = PostSerializer(post)
                return Response(serializer.data, status=200)

            elif post.visibility == 2:  # FRIENDS
                # Friends-only posts require authentication
                if not request.user.is_authenticated:
                    return HttpResponse("Friends-only posts must be authenticated to view.", status=403)
                # Check if the request user is the author or a friend of the author
                if request.user != author and request.user not in author.friends.all():
                    return HttpResponse("You do not have permission to view this friend's post.", status=403)
                
                # If permission is granted, serialize and return the post
                serializer = PostSerializer(post)
                return Response(serializer.data, status=200)

            elif post.visibility == 3:  # UNLISTED
                # Unlisted posts require authentication
                if not request.user.is_authenticated:
                    return HttpResponse("Unlisted posts must be authenticated to view.", status=403)
                
                # If authenticated, return the post
                serializer = PostSerializer(post)
                return Response(serializer.data, status=200)

            elif post.visibility == 4:  # DELETED
                # Deleted posts should return a 404 error
                if request.user.is_authenticated:
                    requestUser = get_object_or_404(User, uuid=request.user.uuid)
                    if requestUser.is_staff:
                        serializer = PostSerializer(post)
                        return Response(serializer.data, status = 200)             
                return HttpResponse("This post does not exist.", status=404) # We don't want to disclose information that this post still exists technically
        
    @extend_schema(
        summary="Edit a post",
        description="Edit a specific Post object by a combination of `author_serial` and `post_serial`. Returns a 404 if not found.",
        parameters=[
            OpenApiParameter(
                name='author_serial',
                description='UUID of the Author of the Post to retrieve',
                type=str,
                required=True,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name='post_serial',
                description='UUID of the Post to retrieve',
                type=str,
                required=True,
                location=OpenApiParameter.PATH
            ),
        ],
        request=PostSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=PostSerializer, description='Post retrieved successfully'),
            status.HTTP_404_NOT_FOUND:
            OpenApiResponse(description='Post or Author not found.'),
        },
        tags=['Posts API']
    )
    def put(self, request, author_serial, post_serial):
        """
        PUT [local] update a post
            - local posts: must be authenticated locally as the author
        """
        # make sure the author exists
        if not User.objects.filter(uuid=author_serial).exists(): 
            return Response("Author does not exist.", status=404)  
        
        # check if user is authenticated
        if not request.user.is_authenticated:     
            return Response("You must be authenticated to edit a post.", status=403)
        
        author = User.objects.get(uuid=author_serial) 
        # retrieve the specific post by the author where visibility is not deleted
        try:
            post = Post.objects.get(user=author, uuid=post_serial, visibility__in=[1, 2, 3])
        except Post.DoesNotExist:
            return Response("Post does not exist.", status=404)

        # authenticate the user
        if post.user.uuid != request.user.uuid:
            return Response("You are not the author of this post.", status=403)
        else:
            # update the post fields with request data (fallback to current values if not provided)
            post.title = request.data.get('title', post.title)
            post.content = request.data.get('content', post.content)
            post.description = request.data.get('description', post.description)
            post.visibility = request.data.get('visibility', post.visibility)
            post.modified_at = request.data.get('modified_at', post.modified_at)
            post.modified_at = timezone.now()  # update the modified time

            post.save()

            # return the updated post data using the serializer
            return Response(PostSerializer(post).data, status=200)
    
    @extend_schema(
        summary="Delete a post",
            description="Delete a specific Post object by a combination of `author_serial` and `post_serial`. Returns a 404 if not found.",
            parameters=[
                OpenApiParameter(
                    name='author_serial',
                    description='UUID of the Author of the Post to retrieve',
                    type=str,
                    required=True,
                    location=OpenApiParameter.PATH
                ),
                OpenApiParameter(
                    name='post_serial',
                    description='UUID of the Post to retrieve',
                    type=str,
                    required=True,
                    location=OpenApiParameter.PATH
                ),
            ],
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                    description="Successfully deleted post",
                    response={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Successfully deleted post"
                            }
                        }
                    }
                ),
                status.HTTP_404_NOT_FOUND:
                    OpenApiResponse(description='Post or Author not found.'),
            },
            tags=['Posts API']
    )
    def delete(self, request, post_serial, author_serial):
        """
        DELETE [local] remove a post
            - local posts: must be authenticated locally as the author
        """
        if not User.objects.filter(uuid=author_serial).exists():
            return Response("Author does not exist.", status=404)

        if not request.user.is_authenticated:     
            return Response("You must be authenticated to delete a post.", status=403)
           
        # TODO: check if node admin   
           
        # TODO: check if the author owns the post
                
        post = get_object_or_404(Post, uuid=post_serial)
        if post.user.uuid == request.user.uuid:
            post.visibility = 4
            post.save()
            return Response({
                "message": f"Deleted {post_serial}"
            }, status=200)
        else:
            return Response("You are not the author of this post.", status=403)

class PostsPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "type": "posts",
            "page_number": self.page.number,
            "size": self.page.paginator.per_page,
            "count": self.page.paginator.count,
            "src": data,
        })

class AuthorPostsAllView(APIView):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/posts
    """
    pagination_provider = PostsPagination

    @extend_schema(
        summary="Get all posts from author AUTHOR_SERIAL (paginated)",
        description="Get all posts from author AUTHOR_SERIAL (paginated).",
        parameters=[
            OpenApiParameter(
                name='author_serial',
                description='UUID of the Author of the Post to retrieve',
                type=str,
                required=True,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name='page',
                description='Page number',
                type=int,
                required=False,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='size',
                description='Number of items per page',
                type=int,
                required=False,
                location=OpenApiParameter.QUERY
            )
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=PostSerializer(many=True), description='Posts retrieved successfully'),
            status.HTTP_404_NOT_FOUND:
            OpenApiResponse(description='Author not found.'),
        },
        tags=['Posts API']
    )
    def get(self, request, author_serial):
        """
        GET [local, remote] get the recent posts from author AUTHOR_SERIAL (paginated)
            - Not authenticated: only public posts.
            - Authenticated locally as author: all posts.
            - Authenticated locally as friend of author: public + friends-only posts.
            - Authenticated as remote node: This probably should not happen. Remember, the way remote node becomes aware of local posts is by local node pushing those posts to inbox, not by remote node pulling.

        URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/
        """
        if not author_serial:
            return Response("Need to specify at least an author ID", status=400)
        
        author = get_object_or_404(User, uuid=author_serial)

        self.fetch_github_activity(author)

        posts = Post.objects.filter(user=author).filter(visibility__in=[1, 2, 3]).order_by('-created_at')
        # Likes and Comments will be handled in PostSerializer below

        if request.user.is_authenticated:
            if request.user == author:  # "I want to view my own public profile page"
                pass
            else:
                # Retrieve the followees (users the current user who made the request is following)
                followee_uuids = Follow.objects.filter(local_follower=request.user).values_list('local_followee', flat=True)
                followees = User.objects.filter(uuid__in=followee_uuids)

                friends = Follow.objects.filter(
                    local_followee=request.user,
                    local_follower__in=followees
                ).values_list('local_follower_id', flat=True)

                if author.uuid in friends:
                    posts = posts.filter(visibility__in=[1, 2])
                else:
                    # The user who made the request has no relationship with the author whose profile page they want to view
                    posts = posts.filter(visibility=1)
        else:
            # Unauthenticated users should only see public posts
            posts = posts.filter(visibility=1)
        
        pagination = self.pagination_provider()
        page = pagination.paginate_queryset(posts, request)
        serialized_posts = PostSerializer(page, many=True).data

        return pagination.get_paginated_response(serialized_posts)
    
    @extend_schema(
        summary="Create a new post",
        description="Create a new post. Currently, likes and comments are not created since there's no reason to have likes, comments, etc. because it doesn't exist yet",
        request=PostSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(response=PostSerializer, description='Post created successfully'),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Bad request'),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Unauthorized'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description='Internal server error'),
        },
        tags=['Posts API']
    )
    def post(self, request, author_serial):
        """
        POST [local] create a new post but generate a new ID
            - Authenticated locally as author
        
        BODY = 
            {
                "type": "post",
                "title": "A Test Post Title",
                "description": "This is a test post.",
                "contentType": "text/plain",
                "content": "This is the content of the post.",
                "published": "2015-03-09T13:07:04+00:00",
                "visibility": 1
            }
        """
        if(not request.user.is_authenticated):
            return Response("You need to be authenticated to create a post.", status=401)
        
        author = User.objects.get(uuid=author_serial)
        author_data = UserSerializer(author).data
        author_data["id"] = author.uuid
        request.data["author"] = author_data
        serializer = CreatePostSerializer(data=request.data, partial=True)

        if serializer.is_valid():
            instance = serializer.save()

            # Serialize the response
            response = CreatePostSerializer(instance).data
            return Response(response, status=status.HTTP_201_CREATED)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
    def fetch_github_activity(self, author):
        """
        Fetch GitHub activity for a user and turns it into a post, only if the activity is not already in the database as a post.
        """
        if(not author.github):
            return
        
        author_github_username = author.github.split("/")[-1]

        api = f"https://api.github.com/users/{author_github_username}/events"
        response = requests.get(api)
        events = []

        if response.status_code == 200:
            events = response.json()

        for event in events:
            if(not Post.objects.filter(github_id=event["id"]).exists()):
                event_post = self.generate_post_data(event)
                author_data = UserSerializer(author).data
                author_data["id"] = author.uuid
                event_post["author"] = author_data

                serializer = CreatePostSerializer(data=event_post)
                if serializer.is_valid():
                    serializer.save()
                else:
                    print("Error saving post:", serializer.errors)
    
    def generate_post_data(self, event):
        """
        Generate post data from GitHub event data.
        """
        event_type = event['type']
        actor = event['actor']['login']
        repo_name = event['repo']['name']
        created_at = event['created_at']
        
        title, description, content = "Github Event", "Github Event", "Github Event"

        if event_type == "CommitCommentEvent":
            comment = event['payload']['comment']
            title = f"{actor} commented on a commit in {repo_name}"
            description = f"Comment by {actor} on commit."
            content = comment.get("body", "")

        elif event_type == "CreateEvent":
            ref_type = event['payload'].get('ref_type', 'repository')
            ref = event['payload'].get('ref', '')
            title = f"Created a new {ref_type} in {repo_name}"
            description = f"{actor} created a {ref_type} named {ref}."
            content = f"{actor} created a {ref_type} '{ref}' in repository '{repo_name}'."

        elif event_type == "DeleteEvent":
            ref_type = event['payload'].get('ref_type', 'repository')
            ref = event['payload'].get('ref', '')
            title = f"Deleted a {ref_type} in {repo_name}"
            description = f"{actor} deleted a {ref_type} named {ref}."
            content = f"The {ref_type} '{ref}' in '{repo_name}' was deleted."

        elif event_type == "ForkEvent":
            forkee = event['payload'].get('forkee', {}).get('name', 'forked repo')
            title = f"Forked {repo_name}"
            description = f"{actor} forked the repository {repo_name}."
            content = f"{actor} created a fork of '{repo_name}', resulting in '{forkee}'."

        elif event_type == "GollumEvent":
            pages = event['payload']['pages']
            title = f"{actor} edited wiki pages in {repo_name}"
            description = f"{actor} updated wiki pages in {repo_name}."
            content = "\n".join([f"{page['action'].capitalize()} wiki page: {page['title']}" for page in pages])

        elif event_type == "IssueCommentEvent":
            action = event['payload']['action']
            issue = event['payload']['issue']['title']
            title = f"{actor} {action} a comment on an issue in {repo_name}"
            description = f"Issue '{issue}' has a new comment by {actor}."
            content = event['payload']['comment'].get('body', "")

        elif event_type == "IssuesEvent":
            action = event['payload']['action']
            issue = event['payload']['issue']['title']
            title = f"Issue '{issue}' {action} in {repo_name} by {actor}"
            description = f"{actor} {action} issue '{issue}' in {repo_name}."
            content = f"Issue details: {issue}\nAction taken: {action}."

        elif event_type == "MemberEvent":
            action = event['payload']['action']
            member = event['payload']['member']['login']
            title = f"{actor} {action} {member} to {repo_name}"
            description = f"{member} was {action} by {actor} in {repo_name}."
            content = f"User '{member}' was {action} as a collaborator."

        elif event_type == "PublicEvent":
            title = f"{repo_name} is now public!"
            description = f"{actor} made {repo_name} public."
            content = f"The repository '{repo_name}' was made public."

        elif event_type == "PullRequestEvent":
            action = event['payload']['action']
            pr_number = event['payload']['number']
            title = f"Pull request #{pr_number} {action} in {repo_name}"
            description = f"Pull request #{pr_number} was {action} by {actor}."
            content = f"Details of pull request: #{pr_number}."

        elif event_type == "PushEvent":
            commits = event['payload']['commits']
            title = f"{actor} pushed {len(commits)} commit(s) to {repo_name}"
            description = f"New commits pushed by {actor} to {repo_name}."
            content = "\n".join([f"- {commit['message']}" for commit in commits])

        elif event_type == "ReleaseEvent":
            action = event['payload']['action']
            release = event['payload']['release']['name']
            title = f"Release '{release}' {action} in {repo_name}"
            description = f"{actor} {action} release '{release}' in {repo_name}."
            content = f"Release details: {release}"

        elif event_type == "SponsorshipEvent":
            action = event['payload']['action']
            title = f"Sponsorship {action} by {actor}"
            description = f"{actor} {action} a sponsorship."
            content = f"Sponsorship details: {event['payload']}"

        elif event_type == "WatchEvent":
            title = f"{actor} starred {repo_name}"
            description = f"{actor} starred the repository {repo_name}."
            content = f"User {actor} starred {repo_name}."

        return {
            "title": title,
            "description": description,
            "content": content,
            "created_at": created_at,
            "event_type": event_type,
            "actor": actor,
            "repository": repo_name,
            "contentType": "text/plain",
            "published": created_at,
            "github_id": event["id"],
        }

class PostView(APIView):
    """
    URL: ://service/api/posts/{POST_FQID}
    """

    @extend_schema(
        summary="Get a post",
        description="Get a post",
        parameters=[
            OpenApiParameter(
                name='post_fqid',
                description='Post FQID',
                required=True,
                type=str,
                location='path'
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=PostSerializer, description='Post retrieved successfully'),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Post not found'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description='Internal server error'),
        },
        tags=['Posts API']
    )
    def get(self, request, post_fqid=None):
        """
        GET [local] get the public post whose URL is POST_FQID
            - friends-only posts: must be authenticated
        """
        if post_fqid:
            decoded_post_fqid = unquote(post_fqid)
            post_serial = decoded_post_fqid.split("/")[-1]
            UUID(post_serial)

            post_visibility = ""
            post_data = ""

            print("POST_URL", decoded_post_fqid)

            # Checks for remote first
            parsed_url = urlparse(decoded_post_fqid)
            host = f"{parsed_url.scheme}://{parsed_url.netloc}/api/"

            base_url = f"{settings.BASE_URL}/api/"

            if host!=base_url:
                response = requests.get(decoded_post_fqid)
                data = response.json()  # Parse the JSON response
                post_visibility = data.get("visibility")
                post_data = data
            else:
                post = get_object_or_404(Post, uuid=post_serial)
                post_visibility = post.visibility
                serializer = PostSerializer(post)
                post_data = serializer.data


            # Check the visibility of the post
            if post_visibility in (1, "PUBLIC"): # Anyone can see PUBLIC posts
                pass
            elif post_visibility in (2, 3):  # FRIENDS or UNLISTED
                if not request.user.is_authenticated:
                    return Response("Authentication required to view this post.", status=403)
            elif post_visibility == 4:  # DELETED
                if not (request.user.is_authenticated and request.user.is_staff):
                    return Response("Post does not exist.", status=404) # Don't disclose information for security purposes
            
            return Response(post_data, status=200)
        else:
            return Response("No post ID specified", status=400)
