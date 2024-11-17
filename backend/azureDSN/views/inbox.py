from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiTypes, OpenApiExample, inline_serializer
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse, quote
from ..serializers import *
from ..models import *
import requests, os
from datetime import datetime

'''
a POST request occurs if someone like, comment, share post or send follow request to our local user
a GET request occurs when a local user wants to check her/his inbox
'''
class InboxView(APIView):
    @extend_schema(
        summary="Retrieve Inbox",
        description="Fetch all inbox items for the specified author.",
        parameters=[
            OpenApiParameter(
                name='author_serial', 
                description='UUID of the author whose inbox to retrieve', 
                type=str,  
                required=True,
                location=OpenApiParameter.PATH
            )
        ],
        responses = {
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="InboxResponse",
                    fields={
                        'user': serializers.CharField(),
                        'items': serializers.ListField(
                            child=serializers.JSONField(),  # Use JSONField for flexibility in representing different item types
                            help_text="List of inbox items, which may include Likes, Comments, FollowRequests, or Shares."
                        ),
                        'type': serializers.CharField()
                    }
                ),
                description='Inbox items retrieved successfully',
                examples=[
                    OpenApiExample(
                        "Example Inbox Response",
                        value={
                            "user": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                            "items": [
                                {
                                    "type":"like",
                                    "author":{
                                        "type":"author",
                                        "id":"http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                                        "host":"http://127.0.0.1:8000/azureDSN/",
                                        "displayName":"Quin Nguyen",
                                        "github": "https://github.com/QuinNguyen02",
                                        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                                        "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
                                    },
                                    "published":"2015-03-09T13:07:04+00:00",
                                    "object": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0/posts/c3616cea-959f-4656-b1c4-34f9f39b8197"
                                },
                                {
                                        "type":"comment",
                                        "author":{
                                            "type":"author",
                                            "id":"http://127.0.0.1:8000/api/authors/aa19d08d-e256-45d2-8b9b-b2cef638815e",
                                            "host":"http://127.0.0.1:8000/azureDSN/",
                                            "displayName":"Quin Nguyen",
                                            "github": "https://github.com/QuinNguyen02",
                                            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                                            "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
                                        },
                                        "comment":"Tina comment on Kyle's public post",
                                        "contentType":"text/plain",
                                        "published":"2024-10-30T13:07:04+00:00",
                                        "post": "http://127.0.0.1:8000/api/authors/7104fa38-1129-4f3b-a4e8-8ce6f7552454/posts/0f9bea88-45a8-41c4-95eb-73cb381f2ab5"
                                },
                                {
                                    "type": "share",
                                    "user": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                                    "post": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0/posts/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0"
                                },
                            ],
                            "type": "Inbox"
                        },
                    ),
                ]
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Author not found.",
            ),
        },
        tags=['Inbox API']
    )
    def get(self, request, author_serial):
        action = request.query_params.get('action', None)

        user_obj = get_object_or_404(User, uuid=author_serial)
        inbox_obj = get_object_or_404(Inbox, user=user_obj)
        
        # if action == 'posts':
        # Assuming that `content_object` refers to a Post model, and that it has a 'visibility' field
        # This will only fetch inbox items of type 'post' and visibility 2 or 3
            # post_content_type = ContentType.objects.get(model="post")
            # inbox_items_obj = InboxItem.objects.filter(
            #                                             inbox=inbox_obj,
            #                                             content_type=post_content_type,
            #                                             object_id__in=Post.objects.filter(visibility__in=[2, 3]).values_list('uuid', flat=True)
            #                                         ).order_by("-id")
        # else:
        
        # Get the latest inbox items
        inbox_items_obj =  InboxItem.objects.filter(inbox=inbox_obj).order_by("-time")
        
        serializer = InboxItemSerializer(inbox_items_obj, many=True, context={"request": request})
        # author is return in format of her/his url
        uri = request.build_absolute_uri("/")
        data = {
                'user': f"{uri}api/authors/{author_serial}",
                'items': serializer.data,
                'type': 'inbox',
        }
        return Response(data, status=status.HTTP_200_OK)
    

    @extend_schema(
        summary="Delete Inbox Items",
        description="Delete items from the inbox. If no body is provided, all inbox items are deleted. If a `type` and `id` are provided, the specific post or follow request is deleted.",
        parameters=[
            OpenApiParameter(
                name='author_serial',
                description='UUID of the author whose inbox is being modified.',
                type=str,
                location=OpenApiParameter.PATH,
                required=True
            ),
        ],

        # Define the request body with `type` and `id` as fields in the payload
        request = inline_serializer(
            name="DeleteInboxItemPayload",
            fields={
                "type": serializers.CharField(help_text="Type of the item to delete (e.g., 'post', 'follow')", required=True),
                "id": serializers.CharField(help_text="fqid/id of the item to delete (e.g., post or follow request)", required=True),
            }
        ),
        
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="DeleteInboxResponse",
                    fields={
                        'user': serializers.CharField(),
                        'items': serializers.ListField(
                            child=serializers.JSONField(),  # Use JSONField for flexibility in representing different item types
                            help_text="List of inbox items, which may include Likes, Comments, FollowRequests, or Shares."
                        ),
                        'type': serializers.CharField()
                    }
                ),
                description='It will return the remaning inbox items',
                examples=[
                    OpenApiExample(
                        "Example Delete Inbox Response",
                        value={
                            "user": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                            "items": [
                                {
                                    "type":"like",
                                    "author":{
                                        "type":"author",
                                        "id":"http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                                        "host":"http://127.0.0.1:8000/azureDSN/",
                                        "displayName":"Quin Nguyen",
                                        "github": "https://github.com/QuinNguyen02",
                                        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                                        "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
                                    },
                                    "published":"2015-03-09T13:07:04+00:00",
                                    "object": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0/posts/c3616cea-959f-4656-b1c4-34f9f39b8197"
                                },
                                {
                                        "type":"comment",
                                        "author":{
                                            "type":"author",
                                            "id":"http://127.0.0.1:8000/api/authors/aa19d08d-e256-45d2-8b9b-b2cef638815e",
                                            "host":"http://127.0.0.1:8000/azureDSN/",
                                            "displayName":"Quin Nguyen",
                                            "github": "https://github.com/QuinNguyen02",
                                            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                                            "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
                                        },
                                        "comment":"Tina comment on Kyle's public post",
                                        "contentType":"text/plain",
                                        "published":"2024-10-30T13:07:04+00:00",
                                        "post": "http://127.0.0.1:8000/api/authors/7104fa38-1129-4f3b-a4e8-8ce6f7552454/posts/0f9bea88-45a8-41c4-95eb-73cb381f2ab5"
                                },
                                {
                                    "type": "share",
                                    "user": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                                    "post": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0/posts/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0"
                                },
                            ],
                            "type": "Inbox"
                        },
                    ),
                ]
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="User, inbox, or item not found."),
        },
        tags=['Inbox API']
    )
    def delete(self, request, author_serial):
        '''
        When delete a post, the body is a deleted post object
        When reject/accept a follow request, body is a follow request object
        if payload is empty = no body, we clear the inbox
        '''
        payload = request.data
        
        if not payload:
            # Delete the whole inbox
            user_obj = get_object_or_404(User, uuid=author_serial)
            inbox_obj = get_object_or_404(Inbox, user=user_obj)
            inbox_obj.items.clear()
            return Response({"message": "delete all inbox items successfully"}, status=status.HTTP_200_OK)
        
        if "type" not in payload:
            return Response({"error": "A 'type' field is required in the inbox delete object request"}, status=status.HTTP_400_BAD_REQUEST)
        
        if payload["type"].lower() == "post":   
            return self.delete_post(author_serial, request)
        elif payload["type"].lower() == "follow":
            return self.delete_follow_request(author_serial, payload, request)
        else:
            return Response({"message": "A 'type' field must be either follow or doesn't included"}, status=status.HTTP_400_BAD_REQUEST)
    
    '''
    The deleted post might be local or remote
    '''
    def delete_post(self, author_serial, request):
        '''
        We can't send directly to remote inbox => we have to send it from our backend
        Idea is to send the whole post obj that is deleted with the receiver object
        The backend itself has to check if the author_serial exists in the User model
            - if exists => local user:
                + for local user, we have to further check if the post send to us is remote post or local post
                    > local post:
                        + Create another inbox item with type post, post_status is delete
                        + Find all the previous post with matching post_id and remove it (handle edited post)
                    > remote post:
                        + Create another inbox item with with remote payload, post_status is delete
                        + Find all the previous post with matching post_id and remove it (handle edited post)
            - if objet does not exist => remote user:
                + we just simply send a delete request with a whole deleted post obj to their endpoint
        return message indicating successful or not
        '''
        payload = request.data
       
        if "type" not in payload:
            return Response({"message": "A 'type' field is required in the inbox post request"}, status=status.HTTP_400_BAD_REQUEST)
        
        try: 
            user_object = User.objects.get(uuid=author_serial)
            inbox_obj = get_object_or_404(Inbox, user=user_object)
            
            # author_serial is local user
            if "follower" in payload:
                del payload["follower"] # we not sure if follower is sent with or not but local user won't need it anyway
            
            try: 
                parsed_url = urlparse(payload["id"]) 
                post_id = parsed_url.path.split("/")[-1] # extract id of the post (the uuid)
                post_obj = Post.objects.get(uuid=post_id)
                
                # Find the old version of that posts in inbox including null, update, update-old or even delete and remove them
                post_content_type = ContentType.objects.get(model="post")
                InboxItem.objects.filter(
                    inbox=inbox_obj,
                    content_type=post_content_type,
                    object_id=post_id,  # Filtering by the specific post ID
                ).delete()
          
                create_inbox_item(inbox_obj, post_obj, post_status="delete")
                return Response({"message": "We have noticed other users about your deleted post"}, status=status.HTTP_200_OK)
            
            except Post.DoesNotExist: 
                # Find the old version of that posts in inbox including null, update, update-old or even delete and remove them
                InboxItem.objects.filter(
                    inbox=inbox_obj,
                    remote_payload__id=payload["id"],  # Check if remote_payload's id matches the incoming id
                ).delete()
                
                create_inbox_item(inbox_obj, remote_payload=payload, post_status="delete")
                return Response({"message": "We have noticed other users about your deleted post"}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            # author_serial is remote user
            return self.send_modified_post_to_remote(payload, http_method="DELETE")
        
    
    '''
    The deleted follow request can be from remote/local users
    '''
    def delete_follow_request(self, author_serial, payload, request):
        user_object = get_object_or_404(User, uuid=author_serial)
        
        # Validate the follow request object sent with the payload
        try:
            follow_obj = FollowRequest.objects.get(id=payload["id"])
        except FollowRequest.DoesNotExist:
            return Response({"message": "Follow request not found."}, status=status.HTTP_404_NOT_FOUND)
        
        '''
        Here when delete the follow request we need to both delete the inbox_item as well as follow_request item
        We also remove that follow request to our follow request database 
        '''
        inbox_obj = get_object_or_404(Inbox, user=user_object)
        delete_inbox_item(inbox_obj, follow_obj)
        follow_obj.delete()
        return Response(InboxSerializer(inbox_obj, context={"request": request}).data, status=status.HTTP_200_OK)

    
    @extend_schema(
        summary="Update Inbox Item or Remote Payload",
        description="Update an inbox item with the specified post ID. If the post is stored as JSON (remote payload), it will update the remote payload.",
        parameters=[
            OpenApiParameter(
                name='author_serial',
                description='UUID of the author whose inbox is being modified.',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True
            )
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string', 'format': 'uuid', 'description': 'fqid of the post to update'},
                    'title': {'type': 'string', 'description': 'New title of the post', 'maxLength': 255},
                    'content': {'type': 'string', 'description': 'New content of the post'},
                    'visibility': {'type': 'string', 'description': 'New visibility of the post'}
                },
                'required': ['id']
            }
        },
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="Post updated successfully."),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Post or inbox item not found."),
        },
        tags=['Inbox API']
    )
    def put(self, request, author_serial):
        '''
        We can't send directly to remote inbox => we have to send it from our backend
        Idea is to send the whole post obj that is edited with the receiver object
        The backend itself has to check if the author_serial exists in the User model
            - if exists => local user:
                + for local user, we have to further check if the post send to us is remote post or local post
                    > local post:
                        + Create another inbox item with type post, post_status is update
                        + Find the previous post with matching post_id, set post_status to edited
                        + If this is the 2+ times update same post, previous update is called update-old
                    > remote post:
                        + Create another inbox item with with remote payload, post_status is update
                        + Find the previous remote_payload with type post and set post_status to edited
                        + If this is the 2+ times update same post, previous update is called update-old
            - if objet does not exist => remote user:
                + we just simply send a put request with a whole edited post obj to their endpoint
        return message indicating successful or not
        '''
        payload = request.data
       
        if "type" not in payload:
            return Response({"message": "A 'type' field is required in the inbox post request"}, status=status.HTTP_400_BAD_REQUEST)
        
        try: 
            user_object = User.objects.get(uuid=author_serial)
            inbox_obj = get_object_or_404(Inbox, user=user_object)
            
            # author_serial is local user
            if "follower" in payload:
                del payload["follower"] # we not sure if follower is sent with or not but local user won't need it anyway
            
            try: 
                parsed_url = urlparse(payload["id"]) 
                post_id = parsed_url.path.split("/")[-1] # extract id of the post (the uuid)
                post_obj = Post.objects.get(uuid=post_id)
                # Local post: Update inbox and modify existing post status
                # Find the old version of that posts in inbox   
                post_content_type = ContentType.objects.get(model="post")
                inbox_item_obj = InboxItem.objects.filter(
                    inbox=inbox_obj,
                    content_type=post_content_type,
                    object_id=post_id,  # Filtering by the specific post ID
                ).exclude(post_status__in=["delete", "edited"])
                
                # Modify the post_status to edited 
                if inbox_item_obj.exists():
                    for item in inbox_item_obj:
                        item.post_status = "edited"
                        item.save()
                        
                create_inbox_item(inbox_obj, post_obj, post_status="update")
                        
                return Response({"message": "We have noticed other users about your updated post"}, status=status.HTTP_200_OK)
            
            except Post.DoesNotExist: 
                # Remote post: Update inbox and modify existing remote payload status
                # Find the old version of that posts in inbox
                existing_item_obj = InboxItem.objects.filter(
                    inbox=inbox_obj,
                    remote_payload__id=payload["id"],  # Check if remote_payload's id matches the incoming id
                ).exclude(post_status__in=["delete", "edited"])
                
                # Modify the post_status to edited
                if existing_item_obj.exists():
                    for item in existing_item_obj:
                        if (item.post_status == "update"):
                            # this means these are the last update
                            item.post_status = "update-old"
                        else:
                            item.post_status = "edited"
                        item.save()
                
                if "modified_at" not in payload:
                    payload["modified_at"] =  datetime.now().isoformat()
                create_inbox_item(inbox_obj, remote_payload=payload, post_status="update")

                return Response({"message": "We have noticed other users about your updated post"}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            # author_serial is remote user
            return self.send_modified_post_to_remote(payload, http_method="PUT")
    
    def send_modified_post_to_remote(self, payload, http_method):
        try:
            remote_follower = payload["follower"]
            del payload["follower"] # reconstruct payload to post object format

            follower_serial = remote_follower.get("id").rstrip('/').split('/')[-1]
            remote_host = remote_follower.get("host")
            parsed_url = urlparse(remote_host)
            base_host = f"{parsed_url.scheme}://{parsed_url.netloc}"

            if payload["visibility"] == "FRIENDS":
                # Need a check here if remote follower indeed has accepted follow request of post's author in their node
                author = payload["author"]
                encoded_url = quote(author.get('id'), safe='')
                remote_follow_status_url = f"{base_host}/api/authors/{follower_serial}/followers/{encoded_url}"
                
                response = requests.get(
                    remote_follow_status_url,
                    auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD')),
                )

                if response.status_code == 404: # User not a follower of remote follower
                    return Response({"message": "Friends-only post is not sent to remote node."}, status=status.HTTP_200_OK)
            
            # Send the updated/deleted post to the remote inbox
            remote_inbox_url = f"{base_host}/api/authors/{follower_serial}/inbox/"
            response = requests.request(
                method=http_method,
                url=remote_inbox_url,
                json=payload,
                auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD')),
            )

            if response.status_code == 200:
                return Response({"message": "Post successfully sent to remote inbox."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": f"Failed to send post: {response.text}"}, status=response.status_code)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Add Item to Inbox",
        description="Add a new item (post, comment, like, share or follow request) to the inbox.",
        request=FollowRequestSerializer,  # This is the serializer used for the follow request
        parameters=[
            OpenApiParameter(
                name='author_serial', 
                description='UUID of the author receiving the inbox item', 
                type=str, 
                required=True,
                location=OpenApiParameter.PATH
            ),
        ],
        examples=[
            OpenApiExample(
                name="Post Example",
                value={
                        "type": "post",
                        "title": "A post title about a post about web dev",
                        "id": "http://127.0.0.1:8000/api/authors/4b190967-fe45-41be-9814-a3de5d028264/posts/c3616cea-959f-4656-b1c4-34f9f39b8197",
                        "description": "This post is a test",
                        "contentType": "text/plain",
                        "content": "Quin public a post, this notifies kyle's inbox",
                        "author":{
                            "type":"author",
                            "id":"http://127.0.0.1:8000/api/authors/4b190967-fe45-41be-9814-a3de5d028264",
                            "host":"http://127.0.0.1:8000/azureDSN/",
                            "displayName":"Quin Nguyen",
                            "github": "https://github.com/QuinNguyen02",
                            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                            "page": "post_images/Screenshot_2024-10-17_014549.png"
                        },
                        "comments": {},
                        "likes": {},
                        "published": "2024-03-09T13:07:04+00:00",
                        "visibility": "PUBLIC"
                },
                description="Example of adding a post to the inbox."
            ),
            OpenApiExample(
                name="Comment Example",
                value={
                        "type":"comment",
                        "author":{
                            "type":"author",
                            "id":"http://127.0.0.1:8000/api/authors/aa19d08d-e256-45d2-8b9b-b2cef638815e",
                            "host":"http://127.0.0.1:8000/azureDSN/",
                            "displayName":"Quin Nguyen",
                            "github": "https://github.com/QuinNguyen02",
                            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                            "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
                        },
                        "comment":"Tina comment on Kyle's public post",
                        "contentType":"text/plain",
                        "published":"2024-10-30T13:07:04+00:00",
                        "post": "http://127.0.0.1:8000/api/authors/7104fa38-1129-4f3b-a4e8-8ce6f7552454/posts/0f9bea88-45a8-41c4-95eb-73cb381f2ab5"
                },
                description="Example of adding a comment to the inbox."
            ),
            OpenApiExample(
                name="Like Example",
                value={
                        "type":"like",
                        "author":{
                            "type":"author",
                            "id":"http://127.0.0.1:8000/api/authors/4b190967-fe45-41be-9814-a3de5d028264",
                            "host":"http://127.0.0.1:8000/azureDSN/",
                            "displayName":"Quin Nguyen",
                            "github": "https://github.com/QuinNguyen02",
                            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                            "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
                        },
                        "published":"2015-03-09T13:07:04+00:00",
                        "object": "http://127.0.0.1:8000/api/authors/4b190967-fe45-41be-9814-a3de5d028264/posts/c3616cea-959f-4656-b1c4-34f9f39b8197"
                },
                description="Example of adding a like to the inbox."
            ),
            OpenApiExample(
                name="Follow Request Example",
                value={
                        "type": "follow",      
                        "summary":"Quin Nguyen wants to follow Kyle Quach",
                        "actor":{
                            "type":"author",
                            "id":"http://127.0.0.1:8000/api/authors/e2c09099-67ad-4d06-bd00-967ab99025f2",
                            "host":"http://127.0.0.1:8000/azureDSN/",
                            "displayName":"Quin Nguyen",
                            "github": "https://github.com/QuinNguyen02",
                            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                            "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
                        },
                        "object":{
                            "type":"author",
                            "id":"http://127.0.0.1:8000/api/authors/1b7fbe0a-7160-4823-8b24-a24f728b8666",
                            "host":"http://127.0.0.1:8000/azureDSN/",
                            "displayName":"Kyle Quach",
                            "page":"http://127.0.0.1:8000/azureDSN/authors/kyle",
                            "github": "https://github.com/KyleQuach03",
                            "profileImage": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
                        }
                },
                description="Example of adding a follow request to the inbox."
            ),
            OpenApiExample(
                name="Share Example",
                value={
                        "type": "share",      
                        "sharer": "1b7fbe0a-7160-4823-8b24-a24f728b8666",
                        "post": "http://127.0.0.1:8000/api/authors/1b7fbe0a-7160-4823-8b24-a24f728b8666/posts/1b7fbe0a-7160-4823-8b24-a24f728b8666"
                },
                description="Example of adding a share to the share model or inbox if possible."
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='Inbox item added successfully'),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Invalid payload or missing type field'),
        },
        tags=['Inbox API']
    )
    def post(self, request, author_serial):
        '''
        The idea is that on receiving the inbox item, we map it to either post, like, comment or follow_request
        When sending/updating posts, body is a post object
        When sending/updating comments, body is a comment object
        When sending/updating likes, body is a like object
        When sending/updating follow requests, body is a follow object
        All these POST object must have a "type" field
        '''

        # If author_serial does not exist locally, then need to dig through payload to check for the remote host
        # user_obj = get_object_or_404(User, uuid=author_serial)
        payload = request.data
       
        if "type" not in payload:
            return Response({"error": "A 'type' field is required in the inbox post request"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists locally
        try:
            user_obj = User.objects.get(uuid=author_serial)
        except ObjectDoesNotExist:
            # Handle remote author
            if payload["type"].lower() == "follow":
                # Send to remote inbox, passing the payload and remote host information
                return self.send_follow_request_to_remote(payload)
            elif payload["type"].lower() == "post":
                # New post created locally but the followers/friends are remote
                # remote follower info is in the payload
                return self.send_post_to_remote(payload)
            
            elif payload["type"].lower() == "like":
                # To-do: Liking a remote post in my local stream
                pass

            elif payload["type"].lower() == "comment":
                # To-do: Commenting on a remote post in my local stream
                pass

            else:
                return Response({"error": "User not found locally and type not supported for remote authors."}, status=status.HTTP_400_BAD_REQUEST)

        if payload["type"].lower() == "post":
            return self.create_post(user_obj, payload, request)
        elif payload["type"].lower() == "follow":
            return self.create_follow_request(user_obj, payload, request)
        elif payload["type"].lower() == "comment":
            return self.create_comment(user_obj, payload, request)
        elif payload["type"].lower() == "like":
            return self.create_like(user_obj, payload, request)
        elif payload["type"].lower() == "share":
            return self.create_share(user_obj, payload, author_serial)
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
        
    def send_post_to_remote(self, payload):
        try:
            remote_follower = payload["follower"]
            
            # Remove follower from payload to return to original post structure
            del payload["follower"]

            follower_serial = remote_follower.get("id").rstrip('/').split('/')[-1]
            remote_host = remote_follower.get("host")
            parsed_url = urlparse(remote_host)
            base_host = f"{parsed_url.scheme}://{parsed_url.netloc}"

            if payload["visibility"] == "FRIENDS":
                # Need a check here if remote follower indeed has accepted follow request of post's author in their node
                author = payload["author"]
                encoded_url = quote(author.get('id'), safe='')
                remote_follow_status_url = f"{base_host}/api/authors/{follower_serial}/followers/{encoded_url}"
                response = requests.get(
                    remote_follow_status_url,
                    auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD')),
                )

                if response.status_code == 404: # User not a follower of remote follower
                    return Response({"message": "Friends-only post is not sent to remote node."}, status=status.HTTP_200_OK)
            
            
            remote_inbox_url = f"{base_host}/api/authors/{follower_serial}/inbox/"
            response = requests.post(
                remote_inbox_url,
                json=payload,
                auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD')),
            )

            if response.status_code == 200:
                return Response({"message": "Post successfully sent to remote inbox."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": f"Failed to send post: {response.text}"}, status=response.status_code)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
    def send_follow_request_to_remote(self, payload):
        try:
            # Assume the remote host URL is found in the payload under the "object" key
            remote_host = payload["object"].get("host")
            author_serial = payload["object"].get("id").rstrip('/').split('/')[-1]  # Get last part of fqid
            parsed_url = urlparse(remote_host)
            base_host = f"{parsed_url.scheme}://{parsed_url.netloc}"
            remote_inbox_url = f"{base_host}/api/authors/{author_serial}/inbox/"

            response = requests.post(
                remote_inbox_url,
                json=payload,
                auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD')),
            )

            if response.status_code == 200:
                # If successful, make a Follow object in local regardless of whether the remote request is going to be accepted
                local_follower_uuid = payload["actor"].get("id").split('/')[-1]
                
                follow_data = {
                    "local_followee": None,
                    "remote_followee": payload["object"].get("id"),
                    "local_follower": local_follower_uuid,
                    "remote_follower": None
                }

                serializer = FollowSerializer(data=follow_data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"message": "Follow request sent to remote inbox."}, status=status.HTTP_200_OK)
                else:
                    print(serializer.errors)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": f"Failed to send follow request: {response.text}"}, status=response.status_code)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    '''
    payload is a follow request object
    we return the status only cause the they dont need to know what is stored in other person's inbox
    '''
    def create_follow_request(self, user_object, payload, request):

        # If user_object (followee) is local

        # If user_object is remote

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
                                             post=post_obj,
                                             comment=payload["comment"])
        serializer = CommentSerializer(comment_obj, data=payload, context={"request": request})

        if serializer.is_valid():
            comment_instance = serializer.save()
            inbox_obj = get_object_or_404(Inbox, user=user_object)
            create_inbox_item(inbox_obj, comment_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
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
    Here the author_serial is the receiver uuid
    We add into the receiver's inbox as well as create share object in the share model
    If receiver is local we add into inbox + share
    If receiver is remote, we do nothing
    payload is a share object
    payload = {
                post: is fqid of shared post
                sharer: is uuid of sharer
               }
    Now both receiver and user is foreign key of User model
    Receiver can be empty/null meaning if the receiver is not our local user => let it empty/null
    Sender is always triggered by our local node => must always be local user
    '''
    def create_share(self, user_object, payload, author_serial):
        share_uuid = payload.get("sharer")
        post_fqid = payload.get("post")
        sharer_obj = User.objects.get(uuid=share_uuid) # sharer is always local
        
        if User.objects.filter(uuid=author_serial).exists():
            # recevier is local, we add share to both share model and inbox 
            receiver_obj = User.objects.get(uuid=author_serial)
            
            share_obj = Share.objects.create(
                user=sharer_obj,
                post=post_fqid,
                receiver=receiver_obj,
                type="share"
            )
            
            # Serialize and validate
            serializer = ShareSerializer(share_obj, data=payload)
            if serializer.is_valid():
                share_obj = serializer.save()
                
                # Get or create the Inbox for the receiver and add the Share object to it
                inbox_obj = get_object_or_404(Inbox, user=receiver_obj)
                create_inbox_item(inbox_obj, share_obj)
                
                return Response({"message": "Store share successfully"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response({"message": "Don't handle remote user"}, status=status.HTTP_200_OK)
            

'''
This create an inbox item referenced to one of the four model except from case where a post make by a remote user
sending to local nodes, then treat it as a JSON data because we don't want to store/have it in our database
'''
def create_inbox_item(inbox, content=None, remote_payload=None, post_status=None):
    if content:
        content_type = ContentType.objects.get_for_model(content)
        id = getattr(content, 'uuid', getattr(content, 'id', None))
        inbox_item_object = InboxItem.objects.create(content_type=content_type, object_id=id, content_object=content, post_status=post_status)
    else:
        inbox_item_object = InboxItem.objects.create(remote_payload=remote_payload, post_status=post_status)
    inbox.items.add(inbox_item_object)
    
    
    
def delete_inbox_item(inbox, inbox_item_obj):
    # This is to remove the inbox_item from the items list
    for item in inbox.items.all():
        # content_object is the actual object (FollowRequest or Post)
        if item.content_object == inbox_item_obj:
            inbox.items.remove(item)