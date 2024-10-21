from uuid import UUID
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from ..serializers import PostSerializer, InboxItemSerializer
from django.shortcuts import get_object_or_404
from ..models import Post, User, Inbox, InboxItem
from django.contrib.contenttypes.models import ContentType

# TODO if user is admin, also get deleted post

class PublicStreamView(APIView):
    def get(self, request):
        """Retrieve the public posts of the node (currently only working for nodes)"""
        # if author is not authenticated just return the public posts
        public_posts = Post.objects.filter(visibility=1)

        # Sort the posts by the most recent creation date
        public_posts = public_posts.order_by('-created_at')

        # Serialize and return the posts
        serializer = PostSerializer(public_posts, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AuthStreamView(APIView):
    def get(self, request):
        print("Req: ", request)
        print("user: ", request.user)

        if request.user.is_authenticated:
            author_uuid = request.user.uuid
            print(f"the user uuid: {author_uuid}")
            # get author (user) object
            user = get_object_or_404(User, uuid=author_uuid)
            user_inbox = get_object_or_404(Inbox, user=user)

            # Query for unlisted and friends-only posts of this user (visibility=2 and visibility=3)
            unlisted_and_friends_posts = Post.objects.filter(
                visibility__in=[2, 3], 
                user=user
            )
            
            post_content_type = ContentType.objects.get(model="post")
            inbox_items = InboxItem.objects.filter(
                            inbox=user_inbox,
                            content_type=post_content_type,
                            object_id__in=Post.objects.filter(visibility__in=[2, 3]).values_list('uuid', flat=True)
                        ).order_by("-id")
            
            serializer = PostSerializer(unlisted_and_friends_posts, many=True)

            inbox_serializer = InboxItemSerializer(inbox_items, many=True, context={"request": request}) # probably an array

            combined_data = serializer.data + inbox_serializer.data

            combined_data_sorted = sorted(combined_data, key=lambda post: post.get('published'), reverse=True)
            # combined_data_sorted = sorted(combined_data, key=lambda post: post.created_at, reverse=True)

            return Response(combined_data_sorted, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)
            
             

        
