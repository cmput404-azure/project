from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from ..models import User, Post, Comment, Like
from ..serializers import PostSerializer, UserSerializer, CreatePostSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.sessions.models import Session
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
from rest_framework.pagination import PageNumberPagination
from uuid import UUID

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
        # TODO: remote node handling
        if not User.objects.filter(uuid=author_serial).exists(): 
            return Response("Author does not exist.", status=404)

        # If both author and post serials are provided
        if (author_serial and post_serial):
            # Retrieve the author
            author = get_object_or_404(User, uuid=author_serial)
            
            # Retrieve the post
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
                return HttpResponse("This post does not exist.", status=404)
        
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
            post.modified_at = request.data.get('modified_at', post.modified_at)
            post.modified_at = timezone.now()  # update the modified time

            # save the changes
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
                    description="Successfully deleted the post."
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
        # check if user exists
        if not User.objects.filter(uuid=author_serial).exists():
            return Response("Author does not exist.", status=404)

        # check if user is authenticated
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

        # make sure the author exists
        if not User.objects.filter(uuid=author_serial).exists():
            return Response("Author does not exist.", status=404)
        
        # make sure the author exists
        author = get_object_or_404(User, uuid=author_serial)

        # retrieve all posts by the author
        posts = Post.objects.filter(user=author).filter(visibility__in=[1, 2, 3])

        

        comments = Comment.objects.filter(post__in=posts)
        likes = Like.objects.filter(post__in=posts)

        # put the comments into the corresponding post
        for post in posts:
            # comment_serializer = CommentArraySerializer(comments=comments.filter(post=post))
            # post.comments = comment_serializer.get_comments(post)
            # post.likes = likes.filter(post=post)
            post.comments = []
            post.likes = []


        # if user is not authenticated
        if not request.user.is_authenticated:
            posts = posts.filter(visibility=1)
        # if user is authenticated locally as author
        elif request.user == author and request.user.is_authenticated:
            posts = posts.all()
        # if user is authenticated as friend of author
        else:
            posts = posts.filter(visibility__in=[1, 2])
        
        pagination = self.pagination_provider()
        page = pagination.paginate_queryset(posts, request)
        serialized_posts = PostSerializer(page, many=True).data

        
        # return Response(PostSerializer(posts_page, many=True).data, status=200)   
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
        request.data["author"] = author_data

        serializer = CreatePostSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            
            # Serialize the response
            response = CreatePostSerializer(instance).data

            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)

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
            post_serial = post_fqid.split("/")[-1]
            UUID(post_serial)
            post = get_object_or_404(Post, uuid=post_serial)

            # Check the visibility of the post
            if post.visibility == 2 and not request.user.is_authenticated:  # FRIENDS
                return Response("Friend's only posts must be authenticated to view.", status=403)
            if post.visibility == 3 and not request.user.is_authenticated:  # UNLISTED
                return Response("Unlisted posts must be authenticated to view.", status=403)
            if post.visibility == 4:  # DELETED
                return Response("Post does not exist.", status=404)
            
            # Post is public if above conditions are not met
            serializer = PostSerializer(post)
            return Response(serializer.data, status=200)
        else:
            return Response("No post ID specified", status=400)