from uuid import UUID
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from ..serializers import PostSerializer
from django.shortcuts import get_object_or_404
from ..models import Post, User

class StreamView(APIView):
    def get(self, request):
        """Retrieve the stream of posts for the given author"""
        author_uuid = request.query_params.get('uuid', None)

        # Query for public posts in the node
        public_posts = Post.objects.filter(visibility=1)
        

        if (author_uuid):
            user = get_object_or_404(User, uuid=author_uuid) # used to fetch friends-only and unlisted

            # Query for unlisted and friends-only posts of this user (visibility=2 and visibility=3)
            unlisted_and_friends_posts = Post.objects.filter(
                visibility__in=[2, 3], 
                user=user
            )

        combined_posts = public_posts | unlisted_and_friends_posts if author_uuid else public_posts

        # Sort the posts by the most recent creation date
        combined_posts = combined_posts.order_by('-created_at')

        # Serialize and return the posts
        serializer = PostSerializer(combined_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
