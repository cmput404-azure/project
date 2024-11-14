from urllib.parse import unquote
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import User, FollowRequest

class FollowRequestView(APIView):
    def get(self, request, author_serial):
        """
        Returns all follow requests of author with `author_serial` with remote_pending=True.
        """
        follow_requests = FollowRequest.objects.filter(actor__id=str(author_serial), remote_pending=True)

        follow_requests_data = [
            {
                "actor": follow_request.actor,
                "remote_object": follow_request.remote_object,
                "remote_pending": follow_request.remote_pending,
            }
            for follow_request in follow_requests
        ]

        return Response(follow_requests_data, status=status.HTTP_200_OK)
    
    def post(self, request, author_serial):
        """
            Save remote follow requests for polling.
        """
        print("Incoming: ", request.data)
        # Always local follower, remote followee
        local_user = get_object_or_404(User, uuid=author_serial)
        payload = request.data

        actor_data = {
            "type": "author",
            "id": str(local_user.uuid),
            "host": local_user.host,
            "displayName": local_user.display_name,
            "username": local_user.username,
            "bio": local_user.bio,
            "profileImage": local_user.profile_image,
            "github": local_user.github,
            "page": local_user.page
        }

        follow_obj = FollowRequest.objects.create(
            actor=actor_data,
            remote_object=payload['object'],
            remote_pending=True
        )

        return Response({ "Message": "Follow request saved." }, status=status.HTTP_200_OK)
    
    def delete(self, request, author_serial, followee_url):
        followee_url = unquote(followee_url)

        request_obj = FollowRequest.objects.filter(
            actor__id=str(author_serial),
            remote_object__id=followee_url
        )

        request_obj.delete()

        return Response({ "Message:" "Outdated follow request has been deleted." }, status=status.HTTP_200_OK)
        