from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from urllib.parse import urlparse
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiTypes
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers
from django.utils import timezone

from ..serializers import *
from ..models import *
from ..utils import *

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
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="InboxResponse",
                    fields={
                        'user': serializers.CharField(),
                        'items': InboxItemSerializer(many=True),  # Keep the InboxItemSerializer here
                        'type': serializers.CharField()
                    }
                ),
                description='Inbox items retrieved successfully'
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Author not found.')
        }
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
            OpenApiParameter(
                name='type',
                description='Type of the item to delete (e.g., "post", "follow").',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False
            ),
            OpenApiParameter(
                name='id',
                description='ID of the item to delete (e.g., post or follow request).',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False
            ),
        ],
        request=None,  # Request body not required for delete all case
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="Inbox items deleted successfully."),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="User, inbox, or item not found."),
        }
    )
    def delete(self, request, author_serial):
        '''
        The idea is that on receiving the inbox item, we map it to either post, like, comment or follow_request
        We find that object stored in our inbox that delete it
        When delete a post, I expect the type and id of the follow request is sent in the body 
        When reject/accept a follow request, body is a follow request object
        if payload is empty = no body, we clear the inbox
        '''
        user_obj = get_object_or_404(User, uuid=author_serial)
        payload = request.data
        
        if not payload:
            # Delete the whole inbox
            inbox_obj = get_object_or_404(Inbox, user=user_obj)
            inbox_obj.items.clear()
            return Response({"error": "A 'type' field is required in the inbox delete object request"}, status=status.HTTP_200_OK)
        
        if "type" not in payload:
            return Response({"error": "A 'type' field is required in the inbox delete object request"}, status=status.HTTP_400_BAD_REQUEST)
        
        if payload["type"].lower() == "post":
            return self.delete_post(user_obj, payload, request)
        elif payload["type"].lower() == "follow":
            return self.delete_follow_request(user_obj, payload, request)
        else:
            return Response({"error": "A 'type' field must be either follow or post"}, status=status.HTTP_400_BAD_REQUEST)
    
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
                    'id': {'type': 'string', 'format': 'uuid', 'description': 'UUID of the post to update'},
                    'title': {'type': 'string', 'description': 'New title of the post', 'maxLength': 255},
                    'content': {'type': 'string', 'description': 'New content of the post'}
                },
                'required': ['id']
            }
        },
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="Post updated successfully."),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Post or inbox item not found."),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid input.")
        }
    )
    def put(self, request, author_serial):
        user_obj = get_object_or_404(User, uuid=author_serial)
        inbox_obj = get_object_or_404(Inbox, user=user_obj)
        payload = request.data
        
        post_content_type = ContentType.objects.get(model="post")
        inbox_item_obj = InboxItem.objects.filter(
                                                    inbox=inbox_obj,
                                                    content_type=post_content_type,
                                                    object_id=payload['id']  # Filtering by the specific post ID
                                                ).order_by("-id")

        if inbox_item_obj.exists():
            for item in inbox_item_obj:
                # item = inbox_item_obj.content_object
                item.content_object.title = request.data.get('title', item.content_object.title)
                item.content_object.content = request.data.get('content', item.content_object.content)
                item.content_object.visibility = request.data.get('visibility', item.content_object.content)
                item.content_object.modified_at = timezone.now()
                item.content_object.save()
            
            return Response({"message": "Update post successfully."}, status=status.HTTP_200_OK)

        else:
            # No matching inbox item found, store the payload as a JSON object
            existing_item = InboxItem.objects.filter(
            inbox=inbox_obj,
            remote_payload__id=payload['id']  # Check if remote_payload's id matches the incoming id
            ).first()

            if existing_item:
                # Update the remote_payload with the new data
                existing_item.remote_payload['title'] = request.data.get('title', existing_item.remote_payload.get('title'))
                existing_item.remote_payload['content'] = request.data.get('content', existing_item.remote_payload.get('content'))
                existing_item.remote_payload['visibility'] = request.data.get('visibility', existing_item.remote_payload.get('visibility'))
                existing_item.modified_at = timezone.now()  # Optionally update modified_at
                existing_item.save()

                return Response({"message": "Update post successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No post founded"}, status=status.HTTP_404_NOT_FOUND)
        
    
    @extend_schema(
        summary="Add Item to Inbox",
        description="Add a new item (post, comment, like, or follow request) to the inbox.",
        request=PostSerializer,  # This is the serializer used for the POST request body
        parameters=[
            OpenApiParameter(
                name='author_serial', 
                description='UUID of the author receiving the inbox item', 
                type=str, 
                required=True,
                location=OpenApiParameter.PATH
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='Inbox item added successfully'),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Invalid payload or missing type field'),
        }
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
        user_obj = get_object_or_404(User, uuid=author_serial)
        payload = request.data
       
        if "type" not in payload:
            return Response({"error": "A 'type' field is required in the inbox post request"}, status=status.HTTP_400_BAD_REQUEST)

        if payload["type"].lower() == "post":
            return self.create_post(user_obj, payload, request)
        elif payload["type"].lower() == "follow":
            return self.create_follow_request(user_obj, payload, request)
        elif payload["type"].lower() == "comment":
            return self.create_comment(user_obj, payload, request)
        elif payload["type"].lower() == "like":
            return self.create_like(user_obj, payload, request)
        elif payload["type"].lower() == "share":
            return self.create_share(user_obj, payload, request)
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
    We add into the receiver's inbox as well as create share object in the share model
    payload is a share object
    payload = {
                post: is fqid of shared post
                user: is fqid of sender 
               }
    '''
    def create_share(self, user_object, payload, request):
        serializer = ShareSerializer(data=payload)
        # post_author = payload["post"].split('/')[-3]
        # post_author_obj = User.objects.get(uuid = post_author)
        if serializer.is_valid():
            share_obj = serializer.save()
            inbox_obj = get_object_or_404(Inbox, user=user_object)
            create_inbox_item(inbox_obj, share_obj)
            return Response({"message": "Notice post's owner about your share successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
    
'''
This create an inbox item referenced to one of the four model except from case where a post make by a remote user
sending to local nodes, then treat it as a JSON data because we don't want to store/have it in our database
'''
def create_inbox_item(inbox, content=None, remote_payload=None):
    if content:
        content_type = ContentType.objects.get_for_model(content)
        id = getattr(content, 'uuid', getattr(content, 'id', None))
        inbox_item_object = InboxItem.objects.create(content_type=content_type, object_id=id, content_object=content)
    else:
        inbox_item_object = InboxItem.objects.create(remote_payload=remote_payload)
    inbox.items.add(inbox_item_object)
    
    
    
def delete_inbox_item(inbox, inbox_item_obj):
    # This is to remove the inbox_item from the items list
    for item in inbox.items.all():
        # content_object is the actual object (FollowRequest or Post)
        if item.content_object == inbox_item_obj:
            inbox.items.remove(item)