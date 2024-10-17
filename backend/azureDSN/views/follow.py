import uuid
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from rest_framework.views import APIView

from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..serializers.follow_serializer import FollowSerializer
from ..serializers.user_serializer import UserSerializer
from ..models import Follow
from ..models import User
from uuid import UUID
from urllib.parse import quote

class FollowView(APIView):
 
    def get_followers(request, user_id):
        if request.method !="GET":
            return Response(status=405, data="Can only do GET")
        print("here")
        followers = Follow.objects.filter(local_followee_id=user_id)  # Adjust this line based on your Follow model
        serializer = FollowSerializer(followers, many=True)
        return Response(serializer.data)

    def remove_follower(request, actor_id, object_id):
            # remove object_id for actor_id 
        return Response(status=200)

    def decoder(foreign_author):
        pass

    @api_view(['PUT'])
    def add_follower(request, user_id, follower_id):   
        try:
            user = User.objects.get(uuid=user_id)
            follower = User.objects.get(uuid=follower_id)
           
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
        if follower:
            follower_host = follower.host

        follower_local = False
        if follower_host.find('127.0.0.1')!=-1:
            follower_local = True

        follow_data = {
            "local_followee": user if follower_local else None,
            "remote_followee": None,
            "local_follower": follower if follower_local else None,
            "remote_follower": None if follower_local else follower.host,
        }

        serializer = FollowSerializer(data=follow_data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Follower added successfully"}, status=200)
        else:
            return Response(serializer.errors, status=400)

    @api_view(['GET'])
    def check_follower(request, actor_id, object_id):
        if request.method !="GET":
            return Response(status=405, data="Can only do GET")

        return Response(status=200)