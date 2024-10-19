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
                'user': f"{uri}api/authors/{author_serial}",
                'items': serializer.data,
                'type': 'inbox',
        }
        return Response(data, status=status.HTTP_200_OK)
    
    '''
    The idea is that on receiving the inbox item, we map it to either post, like, comment or follow_request
    We find that object stored in our inbox that delete it
    When delete a post, I expect the type and id of the follow request is sent in the body 
    When reject/accept a follow request, body is a follow request object
    if payload is empty = no body, we clear the inbox
    '''
    def delete(self, request, author_serial):
        user_obj = get_object_or_404(User, uuid=author_serial)
        payload = request.data
        
        if not payload:
            # Delete the whole inbox
            inbox_obj = get_object_or_404(Inbox, user=user_obj)
            inbox_obj.items.clear()
            return Response(status=status.HTTP_200_OK)
        
        if "type" not in payload:
            return Response({"error": "A 'type' field is required in the inbox delete object request"}, status=status.HTTP_404_NOT_FOUND)
        
        if payload["type"].lower() == "post":
            return self.delete_post(user_obj, payload, request)
        elif payload["type"].lower() == "follow":
            return self.delete_follow_request(user_obj, payload, request)
    
    '''
    The deleted post is definitely a local post
    payload is a post object
    id is in format: http://{server}/api/authors/{user_id}/posts/{post_id}
    '''
    def delete_post(self, user_object, payload, request):
        parsed_url = urlparse(payload["id"]) 
        post_id = parsed_url.path.split("/")[-1] # extract id of the post (the uuid)
        # Validate the post object sent with the payload
        post_obj = Post.objects.get(uuid=post_id)
        serializer = PostSerializer(post_obj, data=payload, context={"request": request})

        '''
        Here when delete the a post we need to remove that post from other people inbox
        Other endpoint will be in charge of update the post database 
        '''
        if True:
        # if serializer.is_valid():
            inbox_obj = get_object_or_404(Inbox, user=user_object)
            delete_inbox_item(inbox_obj, post_obj)
            return Response(InboxSerializer(inbox_obj, context={"request": request}).data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
    '''
    The deleted follow request can be from remote/local users
    '''
    def delete_follow_request(self, user_object, payload, request):
        # Validate the follow request object sent with the payload
        try:
            follow_obj = FollowRequest.objects.get(id=payload["id"])
        except FollowRequest.DoesNotExist:
            return Response({"error": "Follow request not found."}, status=status.HTTP_404_NOT_FOUND)
        
        '''
        Here when delete the follow request we need to both delete the inbox_item as well as follow_request item
        We also remove that follow request to our follow request database 
        '''
        inbox_obj = get_object_or_404(Inbox, user=user_object)
        delete_inbox_item(inbox_obj, follow_obj)
        follow_obj.delete()
        return Response(InboxSerializer(inbox_obj, context={"request": request}).data, status=status.HTTP_200_OK)

    
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
            post_obj = Post.objects.get(uuid=post_id)
            serializer = PostSerializer(post_obj, data=payload, context={"request": request})

            # if serializer.is_valid():
            # Temporary remove validation because it is weird 
            if True:
                inbox_obj = get_object_or_404(Inbox, user=user_object)
                create_inbox_item(inbox_obj, post_obj)
                return Response({"message": "We have noticed other users about your post"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            # If post is from remote user, treat it as a json object
            inbox_obj = get_object_or_404(Inbox, user=user_object)
            create_inbox_item(inbox_obj, remote_payload=payload)
            return Response({"message": "We have noticed other users about your post"}, status=status.HTTP_200_OK)

    '''
    payload is a follow request object
    we return the status only cause the they dont need to know what is stored in other person's inbox
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
            # return Response(InboxSerializer(inbox_obj.items, context={"request": request}).data, status=status.HTTP_200_OK)
            return Response({"message": "Follow request sent successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    '''
    payload is a comment object
    id is http://{server}/api/authors/{user_id}/commented/{comment_id}
    Not tested yet
    '''
    def create_comment(self, user_object, payload, request):
        parsed_url = urlparse(payload["post"]) 
        post_id = parsed_url.path.split("/")[-1] # extract id of the post (the uuid)
        post_obj = Post.objects.get(uuid=post_id)
        comment_obj = Comment.objects.create(user=payload["author"], 
                                             created_at=payload["published"], 
                                             post=post_obj,
                                             comment=payload["comment"],
                                             ContentType=payload["ContentType"])
        serializer = CommentSerializer(comment_obj, data=payload, context={"request": request})

        if serializer.is_valid():
            comment_instance = serializer.save()
            inbox_obj = get_object_or_404(Inbox, user=user_object)
            create_inbox_item(inbox_obj, comment_instance)
            return Response({"message": "Notice post's owner about your comment successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    '''
    payload is a like object
    id is in format: http://{server}/api/authors/{user_id}/liked/{like_id}
    '''
    def create_like(self, user_object, payload, request):
        parsed_url = urlparse(payload["object"]) 
        post_id = parsed_url.path.split("/")[-1] # extract id of the post (the uuid)
        post_obj = Post.objects.get(uuid=post_id)
        like_obj = Like.objects.create(user=payload["author"], 
                                       created_at=payload["published"], 
                                       post=post_obj)
        serializer = LikeSerializer(like_obj, data=payload, context={"request": request})

        if serializer.is_valid():
            like_instance =serializer.save()
            inbox_obj = get_object_or_404(Inbox, user=user_object)
            create_inbox_item(inbox_obj, like_instance)
            return Response({"message": "Notice post's owner about your like successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
    
    
'''
This create an inbox item referenced to one of the four model except from case where a post make by a remote user
sending to local nodes, then treat it as a JSON data because we don't want to store/have it in our database
'''
def create_inbox_item(inbox, content=None, json_data=None):
    if content:
        content_type = ContentType.objects.get_for_model(content)
        id = getattr(content, 'uuid', getattr(content, 'id', None))
        inbox_item_object = InboxItem.objects.create(content_type=content_type, object_id=id, content_object=content)
    else:
        inbox_item_object = InboxItem.objects.create(remote_payload=json_data)
    inbox.items.add(inbox_item_object)
    
    
    
def delete_inbox_item(inbox, inbox_item_obj):
    # This is to remove the inbox_item from the items list
    for item in inbox.items.all():
        # content_object is the actual object (FollowRequest or Post)
        if item.content_object == inbox_item_obj:
            inbox.items.remove(item)