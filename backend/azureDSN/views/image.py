import base64
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from ..models import User, Post
from uuid import UUID
from rest_framework.response import Response

class ImageView(APIView):
    # This end point decodes image posts as images. This allows the use of image tags in Markdown.
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

        elif post_fqid:
            """
                URL: ://service/api/posts/{POST_FQID}/image
                GET [local, remote] get the public post converted to binary as an image
                return 404 if not an image
            """
            try:
                # Example: "/api/posts/{POST_SERIAL}/image"
                path_parts = post_fqid.strip('/').split('/')
                
                post_serial = path_parts[-2]
                UUID(post_serial) # will raise error if not UUID

            except (IndexError, ValueError):
                return Response(
                    {"detail": "Invalid FQID."}, status=400
                )
            
            post = get_object_or_404(Post, uuid=post_serial)

        if post.has_image:
            # Decode base64 to binary
            binary_image_data = base64.b64decode(post.image_data)
            return Response(binary_image_data, content_type=post.content_type.split(';')[0])
        
        else:
            return Response({"error": "post is not an image."}, status=404)
