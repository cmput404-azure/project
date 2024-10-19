from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from django.http import HttpResponse
from ..models import User, Post
from ..serializers import UserSerializer, PostSerializer
from rest_framework.response import Response
import uuid
from datetime import datetime

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
            pass
            
        # If only author serial is provided
        elif (author_serial):
            pass

        else:
            return HttpResponse("Need to specify at least an author ID", status=400)

    def put(self, request, post_fqid):
        """
        PUT [local] update a post
            - local posts: must be authenticated locally as the author
        """
        post = get_object_or_404(Post, uuid=post_fqid)
        
        # Check if user of request is the author of the post
        if request.user != post.user:
            return HttpResponse("You are not the author of this post.", status=403)
        
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, post_fqid):
        """
        DELETE [local] remove a post
            - local posts: must be authenticated locally as the author
        """
        post = get_object_or_404(Post, uuid=post_fqid)
        
        # Check if user of request is the author of the post
        if request.user != post.user:
            return HttpResponse("You are not the author of this post.", status=403)
        
        post.delete()
        return Response({
            "message": f"Deleted {post_fqid}"
        }, status=200)

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
                return HttpResponse("Friend's only posts must be authenticated to view.", status=403)
            if post.visibility == 3 and not request.user.is_authenticated:  # UNLISTED
                return HttpResponse("Unlisted posts must be authenticated to view.", status=403)
            if post.visibility == 4:  # DELETED
                return HttpResponse("Post does not exist.", status=404)
            
            # Post is public if above conditions are not met
            serializer = PostSerializer(post)
            return Response(serializer.data, status=200)
        else:
            return HttpResponse("No post ID specified", status=400)
        
class PostCreation(APIView):
    
    def get(self, request, author_serial=None):
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

        # if user is not authenticated
        if not request.user.is_authenticated:
            posts = posts.filter(visibility=1)
        # if user is authenticated locally as author
        elif request.user == author and request.user.is_authenticated:
            posts = posts.all()
        # if user is authenticated as friend of author
        else:
            posts = posts.filter(visibility=[1, 2])
        
        return Response(PostSerializer(posts, many=True).data, status=200)       
    
    def post(self, request, author_serial):
        """
        POST [local] create a new post but generate a new ID
            - Authenticated locally as author
        """
        user_obj = get_object_or_404(User, uuid=author_serial)
        
        # Check if user of request is the author of the post
        # if request.user != author:
        #     return HttpResponse("You are not the author of this post.", status=403)

        '''this is the format
        
        post_data =    {
                "type": "post",
                "title": "A Test Post Title",
                "description": "This is a test post.",
                "contentType": "text/plain",
                "content": "This is the content of the post.",
                "author": {
                    "id": "5f577ee2-0ccc-49a4-b3cc-47a8aeb265df",
                    "displayName": "Bob",
                    "host": "http://localhost:8000",
                    "github": "http://github.com/bob",
                    "page": "http://bob.com",
                    "profile_image": "http://localhost:8000/media/profile_images/bob.png"
                },
                "published": "2015-03-09T13:07:04+00:00",
                "visibility": 1
            }
            
        '''
        
        author = UserSerializer(user_obj).data
        

        serializer = PostSerializer(data=post_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)