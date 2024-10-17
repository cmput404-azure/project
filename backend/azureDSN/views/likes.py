from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse 
from ..models import Post, Like
from ..serializers import LikeSerializer
from rest_framework.response import Response

@api_view(['POST'])
def send_like(request, author_serial=None):
    """
    POST [remote]: send a like object to AUTHOR_SERIAL
    """
    pass

@api_view(['GET'])
def get_likes_by_serial(request, author_serial=None, post_serial=None):
    """
    GET [local, remote]:
    a list of likes from other authors on AUTHOR_SERIAL's post POST_SERIAL
    """
    post = get_object_or_404(Post, uuid=post_serial)

    likes = Like.objects.filter(post=post).order_by('-created_at')[:5]
    count = Like.objects.filter(post_id=post).count() # total likes count

    likes = LikeSerializer(likes, many=True).data

    # Temporary
    response_data = {
        "type": "likes",
        "id": f"http://ournodenamehere/api/authors/{author_serial}/posts/{post_serial}/likes",
        "page": f"http://ournodenamehere/authors/{author_serial}/posts/{post_serial}/likes",
        "page_number": 1,
        "size": 50,
        "count": count,
        "src": likes  # List of likes
    }

    return Response(response_data, status=200)

    # # Serialize the response using LikesSerializer
    # likes_response = LikesSerializer(data=likes_data)

    # if likes_response.is_valid():
    #     return HttpResponse(likes_response.data, status=200)
    
    # return HttpResponse(likes_response.errors, status=400)