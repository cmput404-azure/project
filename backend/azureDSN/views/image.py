from urllib.parse import urlparse
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from ..models import User, Post
from uuid import UUID
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import status

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

            # To-do: add a check to ensure the post belongs to that user

        elif post_fqid:
            """
                URL: ://service/api/posts/{POST_FQID}/image
                GET [local, remote] get the public post converted to binary as an image
                return 404 if not an image
            """
            try:
                # Extract the POST FQID's path
                parsed_url = urlparse(post_fqid)
                path_parts = parsed_url.path.strip('/').split('/')
                
                # Check structure to locate post UUID and validate it
                if len(path_parts) >= 5 and path_parts[-2] == 'posts':
                    post_serial = path_parts[-1]
                    UUID(post_serial) 

                else:
                    raise ValueError("Invalid FQID format")

            except (IndexError, ValueError):
                return Response({"detail": "Invalid FQID format."}, status=400)
            
            post = get_object_or_404(Post, uuid=post_serial)

        if post.has_image:
            img_type = post.content_type.split(';')[0]
            data = f"data:{post.content_type},{post.content}"
            
            return Response({"image": data, "content_type": img_type}, status=200)
        
        else:
            return Response({"error": "post is not an image."}, status=404)
