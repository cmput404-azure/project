from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from django.http import HttpResponse
from ..models import User, Post
from ..serializers import UserSerializer, PostSerializer
from rest_framework.response import Response

class PostView(APIView):
    def get(self, request, post_fqid=None):
        """
        GET [local] get the public post whose URL is POST_FQID
            - friends-only posts: must be authenticated
        """

        if post_fqid:
            post = get_object_or_404(Post, uuid=post_fqid)

            # check the visibility of the post
            if post.visibility == 2 and not request.user.is_authenticated: # FRIENDS
                return HttpResponse("Friend's only posts must be authenticated to view.", status=403)
            if post.visibility == 3 and not request.user.is_authenticated: # UNLISTED
                return HttpResponse("Unlisted posts must be authenticated to view.", status=403)
            if post.visibility == 4: # DELETED
                return HttpResponse("Post does not exist.", status=404)
            
            # post is public if aboVe conditions are not met
            serializer = PostSerializer(post)
            return Response(serializer.data, status=200)
        else:
            return HttpResponse("No post ID specified in fqid", status=400)
    
    
class AuthorPostView(APIView):
    def get(self, request, author_serial, post_serial):
        """
        GET [local, remote] get the public post whose serial is POST_SERIAL
            - friends-only posts: must be authenticated
        """

        author = get_object_or_404(User, uuid=author_serial)
        post = get_object_or_404(Post, user=author, uuid=post_serial)

        # Check permissions
        if post.visibility == 2 and not request.user.is_authenticated:  # FRIENDS
            return HttpResponse("Friend's only posts must be authenticated to view.", status=403)
        if post.visibility == 3 and not request.user.is_authenticated:  # UNLISTED
            return HttpResponse("Unlisted posts must be authenticated to view.", status=403)
        if post.visibility == 4:  # DELETED
            return HttpResponse("Post does not exist.", status=404)
        
        serializer = PostSerializer(post)
        return Response(serializer.data, status=200)

    def put(self, request, post_fqid):
        """
        PUT [local] update a post
            - local posts: must be authenticated locally as the author
        """
        #TODO: Logic for the PUT request


        return HttpResponse({
            "message": f"Updating {post_fqid}"
        })
    
    def delete(self, request, post_fqid):
        """
        DELETE [local] remove a
            - local posts: must be authenticated locally as the author
        """
        #TODO: Logic for the DELETE request

        return HttpResponse({
            "message": f"Deleted {post_fqid}"
        })
        
class PostCreation(APIView):
    def get (self, request):
        """
        GET [local, remote] get the recent posts from author AUTHOR_SERIAL (paginated)
        - Not authenticated: only public posts.
            - Authenticated locally as author: all posts.
            - Authenticated locally as friend of author: public + friends-only posts.
            - Authenticated as remote node: This probably should not happen. Remember, the way remote node becomes aware of local posts is by local node pushing those posts to inbox, not by remote node pulling.
        """
        
        
    def post(self, request):
        """
        POST [local] create a new post but generate a new ID
            - Authenticated locally as author
        """
