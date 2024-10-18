from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from urllib.parse import urlparse

from ..serializers import *
from ..models import *
from ..utils import *

'''
a POST request occurs if someone like, comment, share post or send follow request to our local user
a GET request occurs when a local user wants to check her/his inbox
'''
class InboxView(APIView):
    methods = ["get", "post"]
    query = InboxItem.objects.all()
    serializer = InboxItemSerializer
    
    
    '''
    When user want to check their inbox, we fetch all objects relating to that user_id
    '''
    def get(self, request, author_serial):
        user_obj = get_object_or_404(User, uuid=author_serial)
        inbox_obj = get_object_or_404(Inbox, user=user_obj)
        # Get the latest inbox items
        inbox_items_obj =  InboxItem.objects.filter(inbox=inbox_obj).order_by("-id")
    
        serializer = InboxItemSerializer(inbox_items_obj, many=True, context={"request": request})
        # author is return in format of her/his url
        uri = request.build_absolute_uri("/")
        data = {
                'type': 'inbox',
                'items': serializer.data,
                'author': f"{uri}api/authors/{author_serial}"
        }
        return Response(data)
    
    '''
    The idea is that on receiving the inbox item, we map it to either post, like, comment or follow_request
    When sending/updating posts, body is a post object
    When sending/updating comments, body is a comment object
    When sending/updating likes, body is a like object
    When sending/updating follow requests, body is a follow object
    All these POST object must have a "type" field
    '''
    def post(self, request, author_serial):
        user_obj = get_object_or_404(User, uuid=author_serial)
        payload = request.data
       
        if "type" not in payload:
            return Response({"error": "A 'type' field is required in the inbox post request"}, status=status.HTTP_404_NOT_FOUND)

        if payload["type"].lower() == "post":
            return self.create_post(user_obj, payload, request)
        elif payload["type"].lower() == "follow":
            return self.create_follow_request(user_obj, payload, request)
        elif payload["type"].lower() == "comment":
            return self.create_comment(user_obj, payload, request)
        elif payload["type"].lower() == "like":
            return self.create_like(user_obj, payload, request)
        else:
            return Response(
                {"detail": "Invalid type or unhandled type in request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    '''
    add post to database (if from local user) first then make a request to inbox
    payload is a post object
    id is in format: http://{server}/api/authors/{user_id}/posts/{post_id}
    '''
    def create_post(self, user_object, payload, request):
        try:
            parsed_url = urlparse(payload["id"]) 
            post_id = parsed_url.path.split("/")[-1] # extract id of the post (the uuid)
            # Validate the post object sent with the payload
            post_obj = Post.objects.get(post_id=post_id)
            serializer = PostSerializer(post_obj, data=payload, context={"request": request})

            if serializer.is_valid():
                inbox_obj = get_object_or_404(Inbox, user=user_object)
                create_inbox_item(inbox_obj, post_obj)
                return Response(InboxSerializer(inbox_obj, context={"request": request}).data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            # If post is from remote user, treat it as a json object
            inbox_obj = get_object_or_404(Inbox, user=user_object)
            create_inbox_item(inbox_obj, remote_payload=payload)
            return Response(InboxSerializer(inbox_obj, context={"request": request}).data, status=status.HTTP_201_CREATED)

    '''
    payload is a follow request object
    '''
    def create_follow_request(self, user_object, payload, request):
        # Validate the follow request object sent with the payload
        follow_obj = FollowRequest.objects.create(object=user_object, actor=payload["actor"])
        serializer = FollowRequestSerializer(follow_obj, data=payload, context={"request": request})
        if serializer.is_valid():
            '''
            Here when receive the follow request from other user, we add to our local user's inbox
            We also add that follow request to our database 
            '''
            follow_instance = serializer.save()
            inbox_obj = get_object_or_404(Inbox, user=user_object)
            create_inbox_item(inbox_obj, follow_instance)
            return Response(InboxSerializer(inbox_obj, context={"request": request}).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    '''
    add comment to database first then make a request to inbox
    payload is a comment object
    id is http://{server}/api/authors/{user_id}/commented/{comment_id}
    '''
    def create_comment(self, user_object, payload, request):
        # Retrieve the uuid of the comment / comment_id
        parsed_url = urlparse(payload["id"])
        comment_id = parsed_url.path.split("/")[-1]
        # Validate comment object
        comment_obj = get_object_or_404(Comment, comment_id=comment_id)
        serializer = CommentSerializer(comment_obj, data=payload, context={"request": request})

        if serializer.is_valid():
            inbox_obj = get_object_or_404(Inbox, user=user_object)
            create_inbox_item(inbox_obj, comment_obj)
            return Response(InboxSerializer(inbox_obj, context={"request": request}).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    '''
    add like to database first then make a request to inbox
    payload is a like object
    id is in format: http://{server}/api/authors/{user_id}/liked/{like_id}
    This doesnt work for now cause I dont know how to get Like object 
    '''
    def create_like(self, user_object, payload, request):
        pass
    #     parsed_url = urlparse(payload["object"])
    #     like_id = parsed_url.path.split("/")[-1]

    #     # This is the problem, like_id is not a unique key 
    #     like_obj = get_object_or_404(Like, like_id=like_id) 
    #     serializer = LikeSerializer(instance=like_obj, data=payload, context={"request": request})

    #     if serializer.is_valid():
    #         inbox_obj = get_object_or_404(Inbox, user=user_object)
    #         create_inbox_item(inbox_obj, like_obj)
    #         return Response(InboxSerializer(inbox_obj, context={"request": request}).data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
    
    
'''
This create an inbox item referenced to one of the four model except from case where a post make by a remote user
sending to local nodes, then treat it as a JSON data because we don't want to store/have it in our database
'''
def create_inbox_item(inbox, content=None, json_data=None):
    if content:
        content_type = ContentType.objects.get_for_model(content)
        inbox_item_object = InboxItem.objects.create(content_type=content_type, object_id=content.id, content_object=content)
    else:
        inbox_item_object = InboxItem.objects.create(remote_payload=json_data)
    inbox.items.add(inbox_item_object)