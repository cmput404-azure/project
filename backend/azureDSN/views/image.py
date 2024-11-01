import base64
from urllib.parse import urlparse
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from ..models import User, Post
from uuid import UUID
from rest_framework.response import Response

class ImageView(APIView):
    # This end point decodes image posts as images. This allows the use of image tags in Markdown.
    def get(self, request, author_serial=None, post_serial=None, post_fqid=None):
        if (author_serial and post_serial):
            print("i am NOT using fqid")
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
            print("i am using fqid")
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
            print("there is an image in this post")
            print(f"Type of content: {type(post.content)}")
            print(f"Length of content (after): {len(post.content)}")
            
            print(f"What's the type: {post.content_type}")
            img_type = post.content_type.split(';')[0]

            data = f"data:{post.content_type},{post.content}"
            return Response({"image": data, "content_type": img_type}, status=200)
        
        else:
            return Response({"error": "post is not an image."}, status=404)
