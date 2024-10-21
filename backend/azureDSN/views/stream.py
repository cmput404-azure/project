from uuid import UUID
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from ..serializers import PostSerializer, InboxItemSerializer
from django.shortcuts import get_object_or_404
from ..models import Post, User, Inbox, InboxItem
from django.contrib.contenttypes.models import ContentType

class StreamView(APIView):
    def get(self, request):
        """Retrieve the stream of posts for the given author"""
        print("Req: ", request)
        print("user: ", request.user)

        # if author is not authenticated just return the public posts
        public_posts = Post.objects.filter(visibility=1)

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
            
            # Serialize inbox items into posts
            inbox_posts = [item.content_object for item in inbox_items]
            
            combined_posts = public_posts.union(
                unlisted_and_friends_posts, all=True
            )
            combined_posts = list(combined_posts) + inbox_posts

        else:
            combined_posts = public_posts        

        # TODO if user is admin, also get deleted post
        
        

        # combined_posts = public_posts | unlisted_and_friends_posts | box_serializer.data if request.user.is_authenticated else public_posts

        # Sort the posts by the most recent creation date
        # combined_posts = combined_posts.order_by('-created_at')
        combined_posts = sorted(combined_posts, key=lambda post: post.created_at, reverse=True)

        # Serialize and return the posts
        serializer = PostSerializer(combined_posts, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
