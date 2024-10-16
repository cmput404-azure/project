import uuid
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from urllib.parse import urlparse

from ..serializers import *
from ..models import *
from ..utils import *

def create_inbox_item(inbox, content=None, json_data=None):
    if content:
        content_type = ContentType.objects.get_for_model(content)
        inbox_item_object = InboxItem.objects.create(content_type=content_type, object_id=content.id, content_object=content)
    else:
        inbox_item_object = InboxItem.objects.create(unused_payload=json_data)
    inbox.items.add(inbox_item_object)

class InboxView(APIView):
    methods = ["get", "delete", "post"]
    query = InboxItem.objects.all()
    serializer = InboxItemSerializer
    
    '''
    When user want to check their inbox, we fetch all objects relating to that user_id
    '''
    def get(self, request, user_id):
        user_obj = get_object_or_404(User, user_id=user_id)
        inbox_obj = get_object_or_404(Inbox, user_id=user_obj)
        # Get the latest inbox items
        inbox_items_obj =  InboxItem.objects.filter(inbox=inbox_obj).order_by("-id")
    
        serializer = InboxItemSerializer(inbox_items_obj, many=True, context={"request": request})
        # author is return in format of her/his url
        uri = request.build_absolute_uri("/")
        data = {
                'type': 'inbox',
                'items': serializer.data,
                'author': f"{uri}/api/authors/{user_id}"
        }
        return Response(data)
        
    def delete(self, request, user_id):
        pass
    
    '''
    The idea is that on receiving the inbox item, we map it to either post, like, comment or follow_request
    request_data must has the type key
    '''
    def post(self, request, user_id):
        user_obj = get_object_or_404(User, user_id=user_id)
        payload = request.data
       
        if "type" not in payload:
            return Response({"error": "A 'type' field is required in the inbox post request"}, status=status.HTTP_404_NOT_FOUND)

        if payload["type"].lower() == "post":
            return self.create_post_inbox_item(user_obj, payload, request)
        elif payload["type"].lower() == "follow":
            return self.create_follow_request_inbox_item(user_obj, payload, request)
        elif payload["type"].lower() == "comment":
            return self.create_comment_inbox_item(user_obj, payload, request)
        elif payload["type"].lower() == "like":
            return self.create_like_inbox_item(user_obj, payload, request)
        else:
            return Response(
                {"detail": "Invalid type or unhandled type in request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    '''
    The payload format expected from the client's request is:
    user_id, host, display_name, github, page, profile_image
    post_id, title, content, has_image, image, content_type, visibility 
    type: 'post'
    '''
    def create_post_inbox_item(self, user_object, payload, request):
        try:
            parsed_url = urlparse(payload["post_id"]) 
            path_segments = parsed_url.path.split("/")
            post_id = path_segments[path_segments.index("posts") + 1]
            
            post_obj = Post.objects.get(post_id=post_id)
            
            serializer = PostSerializer(post_obj, data=payload, context={"request": request})

            if serializer.is_valid():
                inbox_obj = get_object_or_404(Inbox, user_id=user_object)
                create_inbox_item(inbox_obj, post_obj)
                return Response(InboxSerializer(inbox_obj, context={"request": request}).data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            # If post is from remote user, treat it as a json object
            inbox_obj = get_object_or_404(Inbox, user_id=user_object)
            create_inbox_item(inbox_obj, unused_payload=payload)
            return Response(InboxSerializer(inbox_obj, context={"request": request}).data, status=status.HTTP_201_CREATED)

    '''
    The payload format expected from the client's request is:
    user_id: a user instance representing the receiver
    requester: a user instance representing the requester
    post_id, title, content, has_image, image, content_type, visibility 
    type: 'follow'
    '''
    def create_follow_inbox_item(self, user_object, payload, request):
        follow_obj = FollowRequest.objects.create(user_id=user_object, requester=payload["requester"])
        serializer = FollowRequestSerializer(follow_obj, data=payload, context={"request": request})

        if serializer.is_valid():
            follow_instance = serializer.save()
            inbox_obj = get_object_or_404(Inbox, user_id=user_object)
            create_inbox_item(inbox_obj, follow_instance)
            return Response(InboxSerializer(inbox_obj, context={"request": request}).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        
    
    