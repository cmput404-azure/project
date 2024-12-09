from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.timezone import is_aware, make_aware
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    OpenApiExample,
    inline_serializer,
)
from django.core.exceptions import ObjectDoesNotExist
from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse, quote, urlunparse
import requests, os, json, logging
from ..serializers import *
from ..models import *
from datetime import datetime
from ..utils import url_parser
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

"""
a POST request occurs if someone like, comment, share post or send follow request to our local user
a GET request occurs when a local user wants to check her/his inbox
"""


class InboxView(APIView):
    @extend_schema(
        summary="Retrieve Inbox",
        description="Fetch all inbox items for the specified author.",
        parameters=[
            OpenApiParameter(
                name="author_serial",
                description="UUID of the author whose inbox to retrieve",
                type=str,
                required=True,
                location=OpenApiParameter.PATH,
            )
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="InboxResponse",
                    fields={
                        "user": serializers.CharField(),
                        "items": serializers.ListField(
                            child=serializers.JSONField(),  # Use JSONField for flexibility in representing different item types
                            help_text="List of inbox items, which may include Likes, Comments, FollowRequests, or Shares.",
                        ),
                        "type": serializers.CharField(),
                    },
                ),
                description="Inbox items retrieved successfully",
                examples=[
                    OpenApiExample(
                        "Example Inbox Response",
                        value={
                            "user": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                            "items": [
                                {
                                    "type": "like",
                                    "author": {
                                        "type": "author",
                                        "id": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                                        "host": "http://127.0.0.1:8000/azureDSN/",
                                        "displayName": "Quin Nguyen",
                                        "github": "https://github.com/QuinNguyen02",
                                        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                                        "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png",
                                    },
                                    "published": "2015-03-09T13:07:04+00:00",
                                    "object": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0/posts/c3616cea-959f-4656-b1c4-34f9f39b8197",
                                },
                                {
                                    "type": "comment",
                                    "author": {
                                        "type": "author",
                                        "id": "http://127.0.0.1:8000/api/authors/aa19d08d-e256-45d2-8b9b-b2cef638815e",
                                        "host": "http://127.0.0.1:8000/azureDSN/",
                                        "displayName": "Quin Nguyen",
                                        "github": "https://github.com/QuinNguyen02",
                                        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                                        "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png",
                                    },
                                    "comment": "Tina comment on Kyle's public post",
                                    "contentType": "text/plain",
                                    "published": "2024-10-30T13:07:04+00:00",
                                    "post": "http://127.0.0.1:8000/api/authors/7104fa38-1129-4f3b-a4e8-8ce6f7552454/posts/0f9bea88-45a8-41c4-95eb-73cb381f2ab5",
                                },
                                {
                                    "type": "share",
                                    "user": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                                    "post": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0/posts/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                                },
                            ],
                            "type": "Inbox",
                        },
                    ),
                ],
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Author not found.",
            ),
        },
        tags=["Inbox API"],
    )
    def get(self, request, author_serial):
        user_obj = get_object_or_404(User, uuid=author_serial)
        inbox_obj = get_object_or_404(Inbox, user=user_obj)

        # Get the latest inbox items
        inbox_items_obj = InboxItem.objects.filter(inbox=inbox_obj).order_by("-time")

        serializer = InboxItemSerializer(
            inbox_items_obj, many=True, context={"request": request}
        )
        filtered_data = []
        for json in serializer.data:
            if json.get("type") in ["like", "post", "comment"]:
                base_host = url_parser.get_base_host(json.get("id"))
            elif json.get("type") == "follow":
                base_host = url_parser.get_base_host(json.get("actor").get("id"))

            if (
                base_host.strip().lower() != (settings.BASE_URL).strip().lower()
            ):  # only for remote objects
                try:
                    req = requests.get(
                        f"{base_host}/api/authors/?page=1&size=1",  # Any endpoint to ensure connection
                        auth=HTTPBasicAuth(
                            os.getenv("NODE_USERNAME"), os.getenv("NODE_PASSWORD")
                        ),
                    )

                    if req.status_code == 200:
                        filtered_data.append(json)
                    elif req.status_code == 403:
                        # Local node in remote node's list, but connection not allowed
                        continue
                    else:
                        continue
                except requests.exceptions.RequestException as e:
                    print(f"Error occurred while fetching {base_host}: {e}")
                    continue
            else:  # local objects
                filtered_data.append(json)

        uri = request.build_absolute_uri("/")

        data = {
            "user": f"{uri}api/authors/{author_serial}",
            "items": filtered_data,
            "type": "inbox",
        }
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete Inbox Items",
        description="Delete items from the inbox. If no body is provided, all inbox items are deleted. If a `type` and `id` are provided, the specific post or follow request is deleted.",
        parameters=[
            OpenApiParameter(
                name="author_serial",
                description="UUID of the author whose inbox is being modified.",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
            ),
        ],
        # Define the request body with `type` and `id` as fields in the payload
        request=inline_serializer(
            name="Delete Inbox body",
            fields={"id": serializers.CharField(), "type": serializers.CharField()},
        ),
        examples=[
            OpenApiExample(
                name="Post Body Example",
                value={
                    "author": {
                        "type": "author",
                        "id": "http://localhost:8001/api/authors/e09c9fff-c5dc-4d9d-9fb1-667a564cd3dd",
                        "bio": "",
                        "displayName": "tino",
                        "github": "https://github.com/QuinNguyen02",
                        "host": "http://localhost:8001/api/",
                        "profileImage": "",
                        "username": "tino",
                    },
                    "comments": [],
                    "content": "dfsfdsf",
                    "contentType": "text/plain",
                    "description": "dsfdfsdf",
                    "follower": {
                        "type": "author",
                        "id": "http://localhost:8001/api/authors/a2d00814-ec38-4ea0-a297-7aa64b24a262",
                        "host": "http://localhost:8001/api/",
                    },
                    "id": f"http://localhost:8000/api/authors/a2d00814-ec38-4ea0-a297-7aa64b24a262/posts/a2d00814-ec38-4ea0-a297-7aa64b24a262",
                    "likes": [],
                    "modified_at": "2024-11-17T02:17:33.067586Z",
                    "published": "2024-11-17T02:17:33.022000Z",
                    "title": "second post",
                    "type": "post",
                    "visibility": 3,
                },
                description="Example of deleting a a post in the inbox.",
            ),
            OpenApiExample(
                name="Follow Request Body Example",
                value={"type": "follow", "id": 12},
                description="Example of deleting a follow request in the inbox.",
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="DeleteInboxResponse",
                    fields={
                        "user": serializers.CharField(),
                        "items": serializers.ListField(
                            child=serializers.JSONField(),  # Use JSONField for flexibility in representing different item types
                            help_text="List of inbox items, which may include Likes, Comments, FollowRequests, or Shares.",
                        ),
                        "type": serializers.CharField(),
                    },
                ),
                description="It will return the remaning inbox items",
                examples=[
                    OpenApiExample(
                        "Example Delete Inbox Response",
                        value={
                            "user": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                            "items": [
                                {
                                    "type": "like",
                                    "author": {
                                        "type": "author",
                                        "id": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                                        "host": "http://127.0.0.1:8000/azureDSN/",
                                        "displayName": "Quin Nguyen",
                                        "github": "https://github.com/QuinNguyen02",
                                        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                                        "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png",
                                    },
                                    "published": "2015-03-09T13:07:04+00:00",
                                    "object": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0/posts/c3616cea-959f-4656-b1c4-34f9f39b8197",
                                },
                                {
                                    "type": "comment",
                                    "author": {
                                        "type": "author",
                                        "id": "http://127.0.0.1:8000/api/authors/aa19d08d-e256-45d2-8b9b-b2cef638815e",
                                        "host": "http://127.0.0.1:8000/azureDSN/",
                                        "displayName": "Quin Nguyen",
                                        "github": "https://github.com/QuinNguyen02",
                                        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                                        "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png",
                                    },
                                    "comment": "Tina comment on Kyle's public post",
                                    "contentType": "text/plain",
                                    "published": "2024-10-30T13:07:04+00:00",
                                    "post": "http://127.0.0.1:8000/api/authors/7104fa38-1129-4f3b-a4e8-8ce6f7552454/posts/0f9bea88-45a8-41c4-95eb-73cb381f2ab5",
                                },
                                {
                                    "type": "share",
                                    "user": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                                    "post": "http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0/posts/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                                },
                            ],
                            "type": "Inbox",
                        },
                    ),
                ],
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="User, inbox, or item not found."
            ),
        },
        tags=["Inbox API"],
    )
    def delete(self, request, author_serial):
        """
        When delete a post, the body is a deleted post object
        When reject/accept a follow request, body is a follow request object
        if payload is empty = no body, we clear the inbox
        """
        payload = request.data

        if not payload:
            # Delete the whole inbox
            user_obj = get_object_or_404(User, uuid=author_serial)
            inbox_obj = get_object_or_404(Inbox, user=user_obj)
            inbox_obj.items.clear()
            return Response(
                {"message": "delete all inbox items successfully"},
                status=status.HTTP_200_OK,
            )

        if "type" not in payload:
            return Response(
                {
                    "error": "A 'type' field is required in the inbox delete object request"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if payload["type"].lower() == "post":
            return self.delete_post(author_serial, request)
        elif payload["type"].lower() == "follow":
            return self.delete_follow_request(author_serial, payload, request)
        else:
            return Response(
                {"message": "A 'type' field must be either follow or doesn't included"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    """
    The deleted post might be local or remote
    """

    def delete_post(self, author_serial, request):
        """
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
        """
        payload = request.data

        if "type" not in payload:
            return Response(
                {"message": "A 'type' field is required in the inbox post request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Local post
            user_object = User.objects.get(uuid=author_serial)
            inbox_obj = get_object_or_404(Inbox, user=user_object)

            # author_serial is local user
            if "follower" in payload:
                del payload[
                    "follower"
                ]  # we not sure if follower is sent with or not but local user won't need it anyway

            try:
                post_id = url_parser.extract_uuid(payload.get('id'))
                post_obj = Post.objects.get(uuid=post_id)

                # Find the old version of that posts in inbox including null, update, update-old or even delete and remove them
                post_content_type = ContentType.objects.get(model="post")
                InboxItem.objects.filter(
                    inbox=inbox_obj,
                    content_type=post_content_type,
                    object_id=post_id,  # Filtering by the specific post ID
                ).delete()

                create_inbox_item(inbox_obj, post_obj, post_status="delete")
                return Response(
                    {"message": "We have notified other users about your deleted post"},
                    status=status.HTTP_200_OK,
                )

            except Post.DoesNotExist:
                # Find the old version of that posts in inbox including null, update, update-old or even delete and remove them
                InboxItem.objects.filter(
                    inbox=inbox_obj,
                    remote_payload__id=payload[
                        "id"
                    ],  # Check if remote_payload's id matches the incoming id
                ).delete()

                create_inbox_item(
                    inbox_obj, remote_payload=payload, post_status="delete"
                )
                return Response(
                    {"message": "We have notified other users about your deleted post"},
                    status=status.HTTP_200_OK,
                )

        except User.DoesNotExist:
            # author_serial is remote user
            return self.send_modified_post_to_remote(payload, http_method="DELETE")

    """
    The deleted follow request can be from remote/local users
    """

    def delete_follow_request(self, author_serial, payload, request):
        user_object = get_object_or_404(User, uuid=author_serial)

        # Validate the follow request object sent with the payload
        try:
            follow_obj = FollowRequest.objects.get(id=payload["id"])
        except FollowRequest.DoesNotExist:
            return Response(
                {"message": "Follow request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        """
        Here when delete the follow request we need to both delete the inbox_item as well as follow_request item
        We also remove that follow request to our follow request database 
        """
        inbox_obj = get_object_or_404(Inbox, user=user_object)
        delete_inbox_item(inbox_obj, follow_obj)
        follow_obj.delete()
        return Response(
            InboxSerializer(inbox_obj, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Update Inbox Item or Remote Payload",
        description="Update an inbox item with the specified post ID. If the post is stored as JSON (remote payload), it will update the remote payload.",
        parameters=[
            OpenApiParameter(
                name="author_serial",
                description="UUID of the author whose inbox is being modified.",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
            )
        ],
        request=inline_serializer(
            name="updated post object payload",
            fields={
                "post": PostSerializer(),
                "follower": UserSerializer(),
            },
        ),
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="Post updated successfully."
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Post or inbox item not found."
            ),
        },
        tags=["Inbox API"],
    )
    def put(self, request, author_serial):
        """
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
        """

        payload = request.data

        if "type" not in payload:
            return Response(
                {"message": "A 'type' field is required in the inbox post request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_object = User.objects.get(uuid=author_serial)
            inbox_obj = get_object_or_404(Inbox, user=user_object)

            # author_serial is local user
            if "follower" in payload:
                del payload[
                    "follower"
                ]  # we not sure if follower is sent with or not but local user won't need it anyway

            try:
                post_id = url_parser.extract_uuid(payload.get('id'))
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

                return Response(
                    {"message": "We have notified other users about your updated post"},
                    status=status.HTTP_200_OK,
                )

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
                        if item.post_status == "update":
                            # this means these are the last update
                            item.post_status = "update-old"
                        else:
                            item.post_status = "edited"
                        item.save()

                if "modified_at" not in payload:
                    payload["modified_at"] = datetime.now().isoformat()
                create_inbox_item(
                    inbox_obj, remote_payload=payload, post_status="update"
                )

                return Response(
                    {"message": "We have notified other users about your updated post"},
                    status=status.HTTP_200_OK,
                )

        except User.DoesNotExist:
            # author_serial is remote user
            return self.send_modified_post_to_remote(payload, http_method="PUT")

    def send_modified_post_to_remote(self, payload, http_method):
        try:
            
            remote_follower = payload["follower"]
            del payload["follower"]  # reconstruct payload to post object format

            follower_serial = url_parser.extract_uuid(remote_follower.get("id"))
            base_host = url_parser.get_base_host(remote_follower.get("host"))
            print(f"UPDATED POST JSON to be sent: {payload}")

            if payload["visibility"] == "FRIENDS":
                # Need a check here if remote follower indeed has accepted follow request of post's author in their node
                author = payload["author"]
                encoded_url = quote(author.get("id"), safe="")
                remote_follow_status_url = (
                    f"{base_host}/api/authors/{follower_serial}/followers/{encoded_url}"
                )

                response = requests.get(
                    remote_follow_status_url,
                    auth=HTTPBasicAuth(
                        os.getenv("NODE_USERNAME"), os.getenv("NODE_PASSWORD")
                    ),
                )

                if (
                    response.status_code == 404
                ):  # User not a follower of remote follower
                    return Response(
                        {"message": "Friends-only post is not sent to remote node."},
                        status=status.HTTP_200_OK,
                    )
            # For DELETE post, we need to change the visibility to DELETED
            if http_method == "DELETE":
                payload["visibility"] = "DELETED"

            # Send POST request to other group if not sharing same code base with us
            if "azure" not in base_host:
                http_method = "POST"
            print(f"method to be sent: {http_method}")

            # Send the updated/deleted post to the remote inbox
            remote_inbox_url = f"{base_host}/api/authors/{follower_serial}/inbox"
            response = requests.request(
                method=http_method,
                url=remote_inbox_url,
                json=payload,
                auth=HTTPBasicAuth(
                    os.getenv("NODE_USERNAME"), os.getenv("NODE_PASSWORD")
                ),
            )

            if response.status_code == 200:
                return Response(
                    {"message": "Post successfully sent to remote inbox."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": f"Failed to send post: {response.text}"},
                    status=response.status_code,
                )

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Add Item to Inbox",
        description="Add a new item (post, comment, like, share or follow request) to the inbox.",
        request=FollowRequestSerializer,  # This is the serializer used for the follow request
        parameters=[
            OpenApiParameter(
                name="author_serial",
                description="UUID of the author receiving the inbox item",
                type=str,
                required=True,
                location=OpenApiParameter.PATH,
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
                    "author": {
                        "type": "author",
                        "id": "http://127.0.0.1:8000/api/authors/4b190967-fe45-41be-9814-a3de5d028264",
                        "host": "http://127.0.0.1:8000/azureDSN/",
                        "displayName": "Quin Nguyen",
                        "github": "https://github.com/QuinNguyen02",
                        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                        "page": "post_images/Screenshot_2024-10-17_014549.png",
                    },
                    "comments": {},
                    "likes": {},
                    "published": "2024-03-09T13:07:04+00:00",
                    "visibility": "PUBLIC",
                },
                description="Example of adding a post to the inbox.",
            ),
            OpenApiExample(
                name="Comment Example",
                value={
                    "type": "comment",
                    "author": {
                        "type": "author",
                        "id": "http://127.0.0.1:8000/api/authors/aa19d08d-e256-45d2-8b9b-b2cef638815e",
                        "host": "http://127.0.0.1:8000/azureDSN/",
                        "displayName": "Quin Nguyen",
                        "github": "https://github.com/QuinNguyen02",
                        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                        "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png",
                    },
                    "comment": "Tina comment on Kyle's public post",
                    "contentType": "text/plain",
                    "published": "2024-10-30T13:07:04+00:00",
                    "post": "http://127.0.0.1:8000/api/authors/7104fa38-1129-4f3b-a4e8-8ce6f7552454/posts/0f9bea88-45a8-41c4-95eb-73cb381f2ab5",
                },
                description="Example of adding a comment to the inbox.",
            ),
            OpenApiExample(
                name="Like Example",
                value={
                    "type": "like",
                    "author": {
                        "type": "author",
                        "id": "http://127.0.0.1:8000/api/authors/4b190967-fe45-41be-9814-a3de5d028264",
                        "host": "http://127.0.0.1:8000/azureDSN/",
                        "displayName": "Quin Nguyen",
                        "github": "https://github.com/QuinNguyen02",
                        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                        "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png",
                    },
                    "published": "2015-03-09T13:07:04+00:00",
                    "object": "http://127.0.0.1:8000/api/authors/4b190967-fe45-41be-9814-a3de5d028264/posts/c3616cea-959f-4656-b1c4-34f9f39b8197",
                },
                description="Example of adding a like to the inbox.",
            ),
            OpenApiExample(
                name="Follow Request Example",
                value={
                    "type": "follow",
                    "summary": "Quin Nguyen wants to follow Kyle Quach",
                    "actor": {
                        "type": "author",
                        "id": "http://127.0.0.1:8000/api/authors/e2c09099-67ad-4d06-bd00-967ab99025f2",
                        "host": "http://127.0.0.1:8000/azureDSN/",
                        "displayName": "Quin Nguyen",
                        "github": "https://github.com/QuinNguyen02",
                        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                        "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png",
                    },
                    "object": {
                        "type": "author",
                        "id": "http://127.0.0.1:8000/api/authors/1b7fbe0a-7160-4823-8b24-a24f728b8666",
                        "host": "http://127.0.0.1:8000/azureDSN/",
                        "displayName": "Kyle Quach",
                        "page": "http://127.0.0.1:8000/azureDSN/authors/kyle",
                        "github": "https://github.com/KyleQuach03",
                        "profileImage": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png",
                    },
                },
                description="Example of adding a follow request to the inbox.",
            ),
            OpenApiExample(
                name="Share Example",
                value={
                    "type": "share",
                    "sharer": "1b7fbe0a-7160-4823-8b24-a24f728b8666",
                    "post": "http://127.0.0.1:8000/api/authors/1b7fbe0a-7160-4823-8b24-a24f728b8666/posts/1b7fbe0a-7160-4823-8b24-a24f728b8666",
                },
                description="Example of adding a share to the share model or inbox if possible.",
            ),
        ],
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                description="Inbox item added successfully"
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid payload or missing type field"
            ),
        },
        tags=["Inbox API"],
    )
    def post(self, request, author_serial):
        """
        The idea is that on receiving the inbox item, we map it to either post, like, comment or follow_request
        When sending/updating posts, body is a post object
        When sending/updating comments, body is a comment object
        When sending/updating likes, body is a like object
        When sending/updating follow requests, body is a follow object
        All these POST object must have a "type" field
        """

        # If author_serial does not exist locally, then need to dig through payload to check for the remote host
        payload = request.data
        print(f"RECEIVED PAYLOAD: {payload}")

        logging.info(f"Entered Post inbox endpoint: {payload}")

        if "type" not in payload:
            return Response(
                {"error": "A 'type' field is required in the inbox post request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
                return self.send_post_to_remote(payload)
            elif payload["type"].lower() == "like":
                print(f"SENDING REMOTE LIKE to uuid {author_serial}")
                return self.send_like_to_remote(payload, request)
            elif payload["type"].lower() == "comment":
                return self.send_comment_to_remote(payload, request)
            else:
                return Response(
                    {
                        "error": "User not found locally and type not supported for remote authors."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Now because all other groups will send a POST request for delete and update post
        # we check if the post's visibility is DELETED => call delete
        # we check if the remote payload in our inbox, if there is one with type post and same id => call update
        if payload["type"].lower() == "post":
            if payload["visibility"].upper() == "DELETED":
                return self.delete_post(author_serial, request)
            else:
                inbox_obj = get_object_or_404(Inbox, user=user_obj)
                # Find the old version of that posts in inbox
                existing_item_obj = InboxItem.objects.filter(
                    inbox=inbox_obj,
                    remote_payload__id=payload[
                        "id"
                    ],  # Check if remote_payload's id matches the incoming id
                )
                if existing_item_obj.exists():
                    # this is the updated remote post so we map to put
                    self.put(request, author_serial)
                else:
                    print(f"CREATE POST LOCALLY")
                    return self.create_post(user_obj, payload, request)
        elif payload["type"].lower() == "follow":
            logging.info("USING LOCAL")
            return self.create_follow_request(user_obj, payload, request)
        elif payload["type"].lower() == "comment":
            print(f"CREATING LOCAL COMMENT")
            return self.create_comment(user_obj, payload, request)
        elif payload["type"].lower() == "like":
            print(f"CREATING LOCAL LIKE")
            return self.create_like(user_obj, payload, request)
        elif payload["type"].lower() == "share":
            return self.create_share(user_obj, payload, author_serial)
        else:
            return Response(
                {"detail": "Invalid type or unhandled type in request."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    """
    add post to database (if from local user) first then make a request to inbox
    payload is a post object
    id is in format: http://{server}/api/authors/{user_id}/posts/{post_id}
    """

    def create_post(self, user_object, payload, request):
        try:
            post_id = url_parser.extract_uuid(payload["id"])

            if post_id.isdigit(): # Handle groups that uses integer as ID
                raise Post.DoesNotExist

            # Validate the post object sent with the payload
            post_obj = Post.objects.get(uuid=post_id)

            inbox_obj = get_object_or_404(Inbox, user=user_object)
            create_inbox_item(inbox_obj, post_obj)
            return Response(
                {"message": "We have notified other users about your post"},
                status=status.HTTP_201_CREATED,
            )

        except Post.DoesNotExist:
            # If post is from remote user, treat it as a JSON object
            inbox_obj = get_object_or_404(Inbox, user=user_object)
            create_inbox_item(inbox_obj, remote_payload=payload)
            return Response(
                {"message": "Remote post received successfully."},
                status=status.HTTP_201_CREATED,
            )

    def validate_inbox_payload(self, payload, is_like=False):
        if is_like:
            required_fields = ["authorId", "object"]
        else:
            required_fields = ["object"]

        errors = []

        # Check for missing or empty required fields
        for field in required_fields:
            if not payload.get(field):
                errors.append(f"'{field}' field is required and cannot be empty.")

        if is_like:
            if payload.get("authorId"):
                    if not url_parser.is_valid_url(payload["authorId"]):
                        errors.append("Author ID is not a valid URL.")
                    elif "api/authors" not in payload["authorId"]:
                        errors.append("Author ID is malformed.")
            
        if payload.get("object"):
            if not url_parser.is_valid_url(payload["object"]):
                errors.append("Object is not a valid URL.")
            elif "api/authors" not in payload["object"]:
                errors.append("Object is malformed.")
        return errors

    def send_post_to_remote(self, payload):
        try:
            remote_follower = payload["follower"]

            # remove follower from payload to return to original post structure
            del payload["follower"]

            follower_serial = url_parser.extract_uuid(remote_follower.get('id'))
            base_host = url_parser.get_base_host(remote_follower.get("host"))
            remote_inbox_url = f"{base_host}/api/authors/{follower_serial}/inbox"

            response = requests.post(
                remote_inbox_url,
                json=payload,
                auth=HTTPBasicAuth(
                    os.getenv("NODE_USERNAME"), os.getenv("NODE_PASSWORD")
                ),
            )

            if response.status_code == 200 or response.status_code == 201:
                return Response(
                    {"message": "Post successfully sent to remote inbox."},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"error": f"Failed to send post: {response.text}"},
                    status=response.status_code,
                )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def send_follow_request_to_remote(self, payload):
        try:
            # Check for object and actor fields
            check_author = payload.get("actor")
            if check_author:
                if not url_parser.is_valid_url(payload["actor"]["id"]):
                    return Response(f"actor id field is invalid", status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(f"author field is missing", status=status.HTTP_400_BAD_REQUEST)

            check_object = payload.get("object")
            if check_object:
                if not url_parser.is_valid_url(payload["object"]["id"]):
                    return Response(f"object id field is invalid", status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(f"object field is missing", status=status.HTTP_400_BAD_REQUEST)

            # Assume the remote host URL is found in the payload under the "object" key
            base_host = url_parser.get_base_host(payload.get('object').get('host'))
            author_serial = url_parser.extract_uuid(payload.get('object').get('id'))

            remote_inbox_url = f"{base_host}/api/authors/{author_serial}/inbox"

            response = requests.post(
                remote_inbox_url,
                json=payload,
                auth=HTTPBasicAuth(
                    os.getenv("NODE_USERNAME"), os.getenv("NODE_PASSWORD")
                ),
            )

            if response.status_code in [200, 201]:
                # If successful, make a Follow object in local regardless of whether the remote request is going to be accepted
                local_follower_uuid = url_parser.extract_uuid(payload.get('actor').get('id'))

                follow_data = {
                    "local_followee": None,
                    "remote_followee": payload["object"].get("id"),
                    "local_follower": local_follower_uuid,
                    "remote_follower": None,
                }

                serializer = FollowSerializer(data=follow_data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {"message": "Follow request sent to remote inbox."},
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    print(serializer.errors)
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {"error": f"Failed to send follow request: {response.text}"},
                    status=response.status_code,
                )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def send_like_to_remote(self, payload, request, test=False):
        # Checks for authorId and object fields
        errors = self.validate_inbox_payload(payload, True)
        if errors:
            print("Payload validation errors:", errors)
            return Response({"error": errors}, status=status.HTTP_400_BAD_REQUEST)
    
        if request and request.user:
            user = User.objects.get(uuid=request.user.uuid)
            payload["author"] = UserSerializer(user).data

        else:
            pass  # Test case, payload author already defined

        # Create like object that references remote post
        try:
            new_like, created = Like.objects.get_or_create(
                user=payload["author"], remote_post=payload["object"]
            )

            if not created:
                return Response(
                {"message": "You already liked this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )

            if created and not test:
                payload["id"] = (
                    f"{url_parser.get_base_host(user.host)}/api/authors/{user.uuid}/liked/{new_like.uuid}"
                )
                created_at = new_like.created_at
                # Ensure timezone-awareness
                if not is_aware(created_at):
                    created_at = make_aware(created_at)

                payload["published"] = created_at.replace(microsecond=0).isoformat()

            base_host = url_parser.get_base_host(
                payload["object"]
            )  # Base host from post FQID
            remote_author_serial = url_parser.extract_uuid(payload["authorId"])
            remote_inbox_api = f"{base_host}/api/authors/{remote_author_serial}/inbox"

            if test:
                return Response(remote_inbox_api, 201)

            del payload["authorId"]  # Don't need this anymore

        except Exception as e:
            return Response(f"Error creating Like object: {e}", status=status.HTTP_400_BAD_REQUEST)

        print(f"FINAL LIKE OBJECT TO BE SENT TO {remote_inbox_api}: {payload}")

        if not url_parser.is_valid_url(payload["id"]):
            return Response(f"id field is invalid: {payload['id']}", status=status.HTTP_400_BAD_REQUEST)

        if not payload["published"]:
            return Response(f"published field is invalid: {payload['published']}", status=status.HTTP_400_BAD_REQUEST)

        try:
            response = requests.post(
                remote_inbox_api,
                auth=HTTPBasicAuth(
                    os.getenv("NODE_USERNAME"), os.getenv("NODE_PASSWORD")
                ),
                json=payload,
            )

            if response.status_code == 200 or response.status_code == 201:
                return Response(
                    {"message": "Like sent to remote inbox."},
                    status=status.HTTP_201_CREATED,
                )

            elif response.status_code == 403:
                return Response(
                    {"message": "Unauthorized on remote node."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def send_comment_to_remote(self, payload, request, test=False):
        print(f"Initial Comment Payload: {payload}")
        if test:
            full_url = request
        else:
            full_url = request.build_absolute_uri()
        parsed_url = urlparse(full_url)

        check_author = payload.get("author")
        if not check_author:
            return Response(f"author field is missing in comments object", status=status.HTTP_400_BAD_REQUEST)

        check_post = payload.get("post")
        if not check_post:
            return Response(f"post field is missing in comments object", status=status.HTTP_400_BAD_REQUEST)

        # Check if request is malformed
        if "api/authors" not in payload["post"]:
            return Response(
                {"error": "Post is malformed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        post_url = payload["post"]
        parsed_post_url = urlparse(post_url)
        author_host = parsed_post_url.netloc

        
        comment_obj = Comment.objects.create(
            user=payload["author"], remote_post=post_url, comment=payload["comment"]
        )
        comment_id = comment_obj.uuid
        created_at = comment_obj.created_at
        if not is_aware(created_at):
            created_at = make_aware(created_at)
        
        comment_url = f"{payload['author']['id']}/commented/{comment_id}"

        payload["contentType"] = "text/plain"
        payload["published"] = created_at.replace(microsecond=0).isoformat()
        payload["post"] = post_url
        payload["id"] = comment_url

        payload_json = json.dumps(payload)
        headers = {
            "Content-Type": "application/json",
            "Content-Length": str(len(payload_json)),
        }
        # Replace the netloc (host) in full_url with author_host
        inbox_url = parsed_url._replace(netloc=author_host)
        formatted_url = urlunparse(inbox_url)

        # checking if payload has all the required fields
        if not url_parser.is_valid_url(payload["id"]):
            return Response(f"id field is invalid: {payload['id']}", status=status.HTTP_400_BAD_REQUEST)

        if not url_parser.is_valid_url(payload["post"]):
            return Response(f"post field is invalid: {payload['post']}", status=status.HTTP_400_BAD_REQUEST)

        if not url_parser.is_valid_url(payload["author"]["id"]):
            return Response(f"The author id in author object is invalid: {payload['author']['id']}", status=status.HTTP_400_BAD_REQUEST)
    
        if test:
            return formatted_url
        
        print(f"FINAL COMMENT PAYLOAD: {payload} to be sent to {author_host}")

        try:
            # Send the POST request
            response = requests.post(
                formatted_url,
                auth=HTTPBasicAuth(os.getenv("NODE_USERNAME"), os.getenv("NODE_PASSWORD")),
                data=payload_json,
                headers=headers,
            )
            
            print(f"Response status code: {response.status_code}")

            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                except requests.JSONDecodeError:
                    print("Response is not valid JSON.")
                    data = {"message": "Successfully sent comment to remote node, but response is not JSON."}
                
                print(f"Returned comment data: {data}") # If remote groups don't send us comment response, gonna fail in frontend
                return Response(payload, response.status_code)
            else:
                return Response(
                    {"error": f"Failed to send comment. Status code: {response.status_code}, Response: {response.text}"},
                    response.status_code,
                )
        except requests.RequestException as e:
            # Handle network-related issues
            print(f"Network error: {str(e)}")
            return Response(
                {"error": f"Network error occurred while sending comment: {str(e)}"},
                500,
            )
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                500,
            )

    """
    payload is a follow request object
    we return the status only cause the they dont need to know what is stored in other person's inbox
    """
    def create_follow_request(self, user_object, payload, request):
        # Validate the follow request object sent with the payload
        follow_obj = FollowRequest.objects.create(
            object=user_object, actor=payload["actor"]
        )
        serializer = FollowRequestSerializer(
            follow_obj, data=payload, context={"request": request}
        )
        if serializer.is_valid():
            """
            Here when receive the follow request from other user, we add to our local user's inbox
            We also add that follow request to our database
            """
            follow_instance = serializer.save()
            inbox_obj = get_object_or_404(Inbox, user=user_object)
            create_inbox_item(inbox_obj, follow_instance)
            return Response(
                {"message": "Follow request sent successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    """
    payload is a comment object
    id is http://{server}/api/authors/{user_id}/commented/{comment_id}
    Not tested yet
    """

    def create_comment(self, user_object, payload, request):
        post_fqid = payload.get('post')
        post_host = url_parser.get_base_host(post_fqid)

        if post_host != settings.BASE_URL.rstrip('/'):
            return Response({"Message": "comment received, not doing anything to it."}, 200) # For cornflowerblue because they are sending back comments to us

        post_id = url_parser.extract_uuid(post_fqid)

        post_obj = Post.objects.get(uuid=post_id)
        comment_obj = Comment.objects.create(
            user=payload["author"], post=post_obj, comment=payload["comment"]
        )
        serializer = CommentSerializer(
            comment_obj, data=payload, context={"request": request}
        )

        if serializer.is_valid():
            comment_instance = serializer.save()
            inbox_obj = get_object_or_404(Inbox, user=user_object)
            create_inbox_item(inbox_obj, comment_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    """
    payload is a like object
    id is in format: http://{server}/api/authors/{user_id}/liked/{like_id}
    """

    def create_like(self, user_object, payload, request):
        from_remote = "authorId" not in payload
        if not from_remote:
            if request and request.user:
                author = User.objects.get(uuid=request.user.uuid)
                payload["author"] = UserSerializer(author).data

            del payload["authorId"]

        post_fqid = payload["object"]
        post_host = url_parser.get_base_host(post_fqid)

        if post_host != settings.BASE_URL.rstrip('/'):
            return Response({"Message": "like received, ignoring..."}, 200) # For cornflowerblue reflective behaviour

        post_id = url_parser.extract_uuid(post_fqid)
        author_id = payload["author"]["id"]
        time = payload.get("published", None)

        try:
            post_obj = Post.objects.get(uuid=post_id)

        except Post.DoesNotExist:
            return Response(
                {"message": "Local Post not found!"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if like already exists
        if Like.objects.filter(user__id=author_id, post=post_obj).exists():
            return Response(
                {"message": "You already liked this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if time:
            like_obj = Like.objects.create(
                user=payload["author"], created_at=time, post=post_obj
            )
        else:
            like_obj = Like.objects.create(user=payload["author"], post=post_obj)

        inbox_obj = get_object_or_404(Inbox, user=user_object)
        create_inbox_item(inbox_obj, like_obj)
        return Response(
            {"message": "Notified post's owner about your like successfully."},
            status=status.HTTP_201_CREATED,
        )

    """
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
    """

    def create_share(self, user_object, payload, author_serial):
        share_uuid = payload.get("sharer")
        post_fqid = payload.get("post")
        sharer_obj = User.objects.get(uuid=share_uuid)  # sharer is always local

        if User.objects.filter(uuid=author_serial).exists():
            # Receiver is local, we add share to both share model and inbox
            receiver_obj = User.objects.get(uuid=author_serial)

            share_obj = Share.objects.create(
                user=sharer_obj, post=post_fqid, receiver=receiver_obj, type="share"
            )

            # Serialize and validate
            serializer = ShareSerializer(share_obj, data=payload)
            if serializer.is_valid():
                share_obj = serializer.save()

                # Get or create the Inbox for the receiver and add the Share object to it
                inbox_obj = get_object_or_404(Inbox, user=receiver_obj)
                create_inbox_item(inbox_obj, share_obj)

                return Response(
                    {"message": "Stored share successfully"},
                    status=status.HTTP_201_CREATED,
                )

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(
                {"message": "Don't handle remote user"}, status=status.HTTP_201_CREATED
            )


"""
This create an inbox item referenced to one of the four model except from case where a post make by a remote user
sending to local nodes, then treat it as a JSON data because we don't want to store/have it in our database
"""


def create_inbox_item(inbox, content=None, remote_payload=None, post_status=None):
    if content:
        content_type = ContentType.objects.get_for_model(content)
        id = getattr(content, "uuid", getattr(content, "id", None))
        inbox_item_object = InboxItem.objects.create(
            content_type=content_type,
            object_id=id,
            content_object=content,
            post_status=post_status,
        )
    else:
        inbox_item_object = InboxItem.objects.create(
            remote_payload=remote_payload, post_status=post_status
        )
    inbox.items.add(inbox_item_object)


def delete_inbox_item(inbox, inbox_item_obj):
    # This is to remove the inbox_item from the items list
    for item in inbox.items.all():
        # content_object is the actual object (FollowRequest or Post)
        if item.content_object == inbox_item_obj:
            inbox.items.remove(item)


class PaginatedInboxView(APIView): 
     @extend_schema(
        summary="Retrieve Inbox with Pagination",
        description="Fetch paginated inbox items for the specified author.",
        parameters=[
            OpenApiParameter(
                name='author_serial',
                description='UUID of the author whose inbox to retrieve',
                type=str,
                required=True,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name='page',
                description='Page number to retrieve',
                type=int,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='size',
                description='Number of items per page',
                type=int,
                required=False,
                location=OpenApiParameter.QUERY,
            )
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="PaginatedInboxResponse",
                    fields={
                        'user': serializers.CharField(),
                        'items': serializers.ListField(
                            child=serializers.JSONField(),
                            help_text="List of paginated inbox items."
                        ),
                        'type': serializers.CharField(),
                        'page': serializers.IntegerField(),
                        'size': serializers.IntegerField(),
                        'total_pages': serializers.IntegerField(),
                        'total_items': serializers.IntegerField(),
                    }
                ),
                description="Paginated Inbox items retrieved successfully",
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Author not found."
            ),
        },
        tags=['Inbox API']
    )
     def get(self, request, author_serial):
        try:
            user_obj = get_object_or_404(User, uuid=author_serial)
            inbox_obj = get_object_or_404(Inbox, user=user_obj)
            inbox_items_obj = InboxItem.objects.filter(inbox=inbox_obj).order_by("-time")

            # Pagination parameters
            page = request.query_params.get('page', 1)
            size = request.query_params.get('size', 5)  # Default size is 5

            paginator = Paginator(inbox_items_obj, size)
            try:
                paginated_items = paginator.page(page)
            except PageNotAnInteger:
                paginated_items = paginator.page(1)
            except EmptyPage:
                paginated_items = []

            serializer = InboxItemSerializer(paginated_items, many=True, context={"request": request})
            
            filtered_data = []
            for json in serializer.data:
                
                if (json == None):
                    continue
                
                if json.get("type") in ["like", "post", "comment"]:
                    base_host = url_parser.get_base_host(json.get('id'))
                elif json.get("type") == "follow":
                    base_host = url_parser.get_base_host(json.get('actor').get('id'))

                if base_host != settings.BASE_URL:
                    try:
                        req = requests.get(
                            f"{base_host}/api/authors/?page=1&size=1",
                            auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD')),
                        )
                        if req.status_code == 200:
                            filtered_data.append(json)
                        elif req.status_code == 403:
                            continue
                    except requests.exceptions.RequestException:
                        continue
                else:
                    filtered_data.append(json)

            uri = request.build_absolute_uri("/")

            data = {
                'user': f"{uri}api/authors/{author_serial}",
                'items': filtered_data,
                'type': 'inbox',
                'page': int(page),
                'size': int(size),
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
            }
            print(data)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"ERROR: {e}")
    
