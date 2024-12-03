from requests.auth import HTTPBasicAuth
from django.conf import settings
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from ..models import User, Post
from uuid import UUID
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import status
from ..utils import url_parser
import os, requests

class ImageView(APIView):
    # This end point decodes image posts as images. This allows the use of image tags in Markdown.
    @extend_schema(
        summary="Retrieve Image Post as Image",
        description=(
            "Retrieve a public post as a binary image by providing either the `author_serial` and "
            "`post_serial`, or a fully qualified post ID (`post_fqid`). Returns a 404 response if "
            "the specified post is not an image or is invalid."
        ),
        parameters=[
            OpenApiParameter(
                name="author_serial",
                description="UUID of the author.",
                required=False,
                type=str,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name="post_serial",
                description="UUID of the post associated with the author.",
                required=False,
                type=str,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name="post_fqid",
                description="Fully qualified ID of the post.",
                required=False,
                type=str,
                location=OpenApiParameter.PATH
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="Image data url successfully retrieved.",
                response={
                    "type": "object",
                    "properties": {
                        "image": {
                            "type": "string",
                            "description": "Image data encoded as a base64 string in full data url.",
                            "example": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA…"
                        },
                        "content_type": {
                            "type": "string",
                            "description": "The MIME type of the image.",
                            "example": "image/png"
                        }
                    }
                }
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="The post is not an image or could not be found.",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "post is not an image."
                        }
                    }
                }
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid FQID format.",
                response={
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "example": "Invalid FQID format."
                        }
                    }
                }
            )
        },
        tags=['Image Posts API']
    )
    def get(self, request, author_serial=None, post_serial=None, post_fqid=None):
        if (author_serial and post_serial):
            """
                URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/image
                GET [local, remote] get the public post converted to binary as an image
                return 404 if not an image
            """
            # Validate incoming data
            author = get_object_or_404(User, uuid=author_serial) # assume local user
            post = get_object_or_404(Post, uuid=post_serial) # assume local posts

            if post.has_image: # This will only be in local DB
                data = f"data:{post.content_type},{post.content}"

                return Response(data, status=200)
            
            else:
                return Response({"error": "post is not an image."}, status=404)

        elif post_fqid:
            """
                URL: ://service/api/posts/{POST_FQID}/image
                GET [local, remote] get the public post converted to binary as an image
                return 404 if not an image
            """
            try:
                # Extract the POST FQID's path
                post_fqid = url_parser.percent_decode(post_fqid)
                post_fqid = post_fqid.rstrip('/')
                if post_fqid.endswith('/image'):
                    post_fqid = post_fqid[:-len('/image')]
                post_serial = url_parser.extract_uuid(post_fqid)
                UUID(post_serial)

            except (IndexError, ValueError):
                return Response({"detail": "Invalid FQID format."}, status=400)
            
            base_host = url_parser.get_base_host(post_fqid)
            if base_host != settings.BASE_URL:
                try:
                    response = requests.get(
                        post_fqid, # if we call the image endpoint, I don't know response structure of other groups
                        auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD')),
                    )

                    if response.status_code == 200:
                        # Reconstruct Image URI using content and contentType
                        post_data = response.json()
                        content_type = post_data.get("contentType") # must be image/png;base64 or image/jpeg;base64 or application/base64
                        content = post_data.get("content")

                        data = f"data:{content_type},{content}"

                        return Response(data, status=200)
                    elif response.status_code == 403:
                        # They don't give us access
                        print(f"Access forbidden to the remote node.")
                        return
                    elif response.status_code == 404:
                        # The remote post/image we are trying to reference isn't an Image Post
                        return Response({"error": "post is not an image."}, status=404)
                    else:
                        return
                except Exception as e:
                    return Response({"Something went wrong."}, status=500)

            else:
                post = get_object_or_404(Post, uuid=post_serial)

                if post.has_image: # This will only be in local DB
                    data = f"data:{post.content_type},{post.content}"

                    return Response(data, status=200)
                else:
                    return Response({"error": "post is not an image."}, status=404)
