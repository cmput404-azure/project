from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Share, User
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers

from ..serializers import ShareSerializer

class ShareView(APIView):
    @extend_schema(
        summary="Check if a User has shared a post",
        description="This endpoint checks if a user has already shared a specific post. It expects `post_fqid` as a query parameter and returns whether the post has been shared by the user.",
        parameters=[
            OpenApiParameter(
                name='author_serial',
                description='UUID of the author (user) whose share status is being checked.',
                type=str,
                required=True,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name='post_fqid',
                description='UUID of the post to check if it has been shared by the user.',
                type=str,
                required=True,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="A response indicating if the post has already been shared by the user.",
                response={
                    "type": "object",
                    "properties": {
                        "exists": {"type": "boolean", "example": True},  # Boolean flag indicating if shared
                    }
                }
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Missing required fields or invalid input."
            ),
        },
        tags=['Share API']
    )
    def get(self, request, author_serial):
        """
        Check whether a user has shared a specific post.
        Expects `post_fqid` as a query parameter and `author_serial` as a path parameter.
        """
        post_fqid = request.query_params.get("post_fqid")

        if not post_fqid:
            return Response({"error": "post_fqid is a required query parameter."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the user object based on author_serial
        user_obj = get_object_or_404(User, uuid=author_serial)

        # Check if a Share object exists with the specified user and post
        share_exists = Share.objects.filter(user=user_obj, post=post_fqid).exists()

        if share_exists:
            return Response({"exists": True}, status=status.HTTP_200_OK)
        else:
            return Response({"exists": False}, status=status.HTTP_200_OK)


    @extend_schema(
        summary="Add a Share item with null receiver",
        description="This endpoint creates a share item for a specific post by a user, even if they have no followers. It expects `post` in the request payload and stores the shared post to track all posts a user has shared.",
        parameters=[
            OpenApiParameter(
                name='author_serial',
                description="UUID of the author (user) who is sharing the post.",
                type=str,
                required=True,
                location=OpenApiParameter.PATH
            ),
        ],
        request = inline_serializer(
            name="share object payload",
            fields={
                "post": serializers.URLField(help_text="fqid of post", required=True),
            }
        ),
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="Indicates that the share has been successfully stored.",
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "Store share successfully"}
                    }
                }
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Missing required fields or invalid input. `post` is a required field."
            ),
        },
        tags=['Share API']
    )
    def post(self, request, author_serial):
        """
        This function is to add a share item where the recevier is null
        Normally share item is created after a share inbox item but this handle the case where user doesn't have any followers
        and we still want to keep track all posts they have shared 
        """
        payload = request.data
        sharer_obj = get_object_or_404(User, uuid=author_serial)
        post_fqid = payload.get("post")

        if not post_fqid:
            return Response({"error": "post is a required field."}, status=status.HTTP_400_BAD_REQUEST)
        
        if Share.objects.filter(user=sharer_obj, post=post_fqid, receiver=None).exists():
            return Response({"error": "can't share duplicate post"}, status=status.HTTP_400_BAD_REQUEST)

        share_obj = Share.objects.create(
                                            user=sharer_obj,
                                            post=post_fqid,
                                            type="share"
                                        )
            
        serializer = ShareSerializer(share_obj, data=payload)
        if serializer.is_valid():
            return Response({"message": "Store share successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

