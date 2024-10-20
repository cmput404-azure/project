from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from ..serializers import PostSerializer
from django.shortcuts import get_object_or_404
from ..models import Post, User

class StreamView(APIView):
    def get(self, request, author_uuid=None):
        """Retrieve the stream of posts for the given author"""
        # user = get_object_or_404(User, uuid=author_uuid) # used later?

        # Query for public posts in the node
        posts = Post.objects.filter(visibility=1)

        # Sort the posts by the most recent creation date
        posts = posts.order_by('-created_at')

        # Serialize and return the posts
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
