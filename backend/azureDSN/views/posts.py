from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from ..models import User, Post, Comment, Like
from ..serializers import PostSerializer, UserSerializer, CreatePostSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse


class AuthorPostView(APIView):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}
    URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/
    """
    
    def get(self, request, author_serial=None, post_serial=None):
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
            
        # If only author serial is provided
        elif (author_serial):
            """
            GET [local, remote] get the recent posts from author AUTHOR_SERIAL (paginated)
                - Not authenticated: only public posts.
                - Authenticated locally as author: all posts.
                - Authenticated locally as friend of author: public + friends-only posts.
                - Authenticated as remote node: This probably should not happen. Remember, the way remote node becomes aware of local posts is by local node pushing those posts to inbox, not by remote node pulling.
                
            URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/
            """
            # make sure the author exists
            author = get_object_or_404(User, uuid=author_serial)

            # retrieve all posts by the author
            posts = Post.objects.filter(user=author)

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
            
            return Response(PostSerializer(posts, many=True).data, status=200)   

        else:
            return Response("Need to specify at least an author ID", status=400)

    def put(self, request, post_fqid):
        """
        PUT [local] update a post
            - local posts: must be authenticated locally as the author
        """
        post = get_object_or_404(Post, uuid=post_fqid)
        
        # Check if user of request is the author of the post
        if request.user != post.user:
            return Response("You are not the author of this post.", status=403)
        
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, post_serial, author_serial):
        """
        DELETE [local] remove a post
            - local posts: must be authenticated locally as the author
        """
        post = get_object_or_404(Post, uuid=post_serial)
        
        # TODO: Check if user of request is the author of the post (Authenticate)
        
        post.delete()
        return Response({
            "message": f"Deleted {post_serial}"
        }, status=200)

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
    def get(self, request, post_fqid=None):
        """
        GET [local] get the public post whose URL is POST_FQID
            - friends-only posts: must be authenticated
        """
        if post_fqid:
            post = get_object_or_404(Post, uuid=post_fqid)

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