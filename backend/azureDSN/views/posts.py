from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from django.http import HttpResponse
from ..models import User, Post
from ..serializers import UserSerializer, PostSerializer

class PostView(APIView):
    def get(self, request, post_fqid=None):
        """
        GET [local] get the public post whose URL is POST_FQID
            - friends-only posts: must be authenticated
        """

        if post_fqid:
            #TODO: Logic for the GET request
            return HttpResponse({
                "message": f"Fetching {post_fqid}"
            })
        else:
            return HttpResponse({
                "message": "No id specified"
            })
    
    
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
        return HttpResponse(serializer.data, status=200)

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