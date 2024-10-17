from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse 
from ..models import Post, Like, User
from ..serializers import LikeSerializer
from rest_framework.response import Response

class SingleLikeView(APIView):
    """Handle retrieval of a single like."""
    def get(self, request, like_fqid=None, author_serial=None, like_serial=None):

        if (like_serial):
            """
            URL: ://service/api/authors/{AUTHOR_SERIAL}/liked/{LIKE_SERIAL}
            GET [local, remote] a single like
            Returns: like object
            """
            print(type(author_serial)) # returns <class 'uuid.UUID'>
            author = get_object_or_404(User, uuid=author_serial)

            like = get_object_or_404(Like, user__id = str(author.uuid), uuid=like_serial)
        
        else:
            """
            URL: ://service/api/liked/{LIKE_FQID}
            GET [local] a single like
            Returns: like object
            """
            # Not yet tested, not sure how to handle FQID yet
            try:
                like_id = like_fqid.split('/')[-1]
            except IndexError:
                return Response(
                    {"detail": "Invalid like FQID."}, status=400
                )
            
            like = get_object_or_404(Like, uuid=like_id)

        serialized_like = LikeSerializer(like).data
        return Response(serialized_like, status=200)
    
class AuthorLikesView(APIView):
    """
    Handle retrieval of Likes by an Author.
    """
    def get(self, request, author_serial=None, author_fqid=None):
        if (author_serial):
            """
            URL: ://service/api/authors/{AUTHOR_SERIAL}/liked
            GET [local, remote] a list of likes by AUTHOR_SERIAL
            Returns: likes object
            """
            print(type(author_serial)) # returns <class 'uuid.UUID'>
            author = get_object_or_404(User, uuid=author_serial)
            likes = Like.objects.filter(user__id=str(author_serial))

        else:
            """
            URL: ://service/api/authors/{AUTHOR_FQID}/liked
            GET [local] a list of likes by AUTHOR_FQID
            Returns: likes object
            """
            print("using fqid")
            author = get_object_or_404(User, uuid=author_fqid.split('/')[-1])
            likes = Like.objects.filter(user__id=str(author.uuid))

        serialized_likes = LikeSerializer(likes, many=True).data
        response = {
            "type": "likes",
            "id": f"the like id FQID?",
            "page": f"the FQID of the page (object) that is liked?",
            "page_number": 1,
            "size": 50,
            "count": len(serialized_likes),
            "src": serialized_likes[:5],  # Limit to first 5 likes
        }

        # to-do: convert the published field into ISO 8601 timestamp
        return Response(response, status=200)


class LikesList(APIView):
    """
    Handle retrieval of Likes on a Post or a Comment.
    """
    def get(self, request, author_serial=None, post_serial=None, post_fqid=None, comment_serial=None):
        pass


# @api_view(['POST'])
# def send_like(request, author_serial=None):
#     """
#     POST [remote]: send a like object to AUTHOR_SERIAL
#     """
#     pass

# @api_view(['GET'])
# def get_likes_by_serial(request, author_serial=None, post_serial=None):
#     """
#     GET [local, remote]:
#     a list of likes from other authors on AUTHOR_SERIAL's post POST_SERIAL
#     """
#     post = get_object_or_404(Post, uuid=post_serial)

#     likes = Like.objects.filter(post=post).order_by('-created_at')[:5]
#     count = Like.objects.filter(post_id=post).count() # total likes count

#     likes = LikeSerializer(likes, many=True).data

#     # Temporary
#     response_data = {
#         "type": "likes",
#         "id": f"http://ournodenamehere/api/authors/{author_serial}/posts/{post_serial}/likes",
#         "page": f"http://ournodenamehere/authors/{author_serial}/posts/{post_serial}/likes",
#         "page_number": 1,
#         "size": 50,
#         "count": count,
#         "src": likes  # List of likes
#     }

#     return Response(response_data, status=200)

#     # # Serialize the response using LikesSerializer
#     # likes_response = LikesSerializer(data=likes_data)

#     # if likes_response.is_valid():
#     #     return HttpResponse(likes_response.data, status=200)
    
#     # return HttpResponse(likes_response.errors, status=400)