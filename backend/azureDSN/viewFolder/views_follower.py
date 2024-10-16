import uuid
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..serializers.follow_serializer import FollowSerializer
from ..serializers.user_serializer import UserSerializer
from ..models import Follow
from ..models import User
from uuid import UUID

@api_view(['GET'])
def get_followers(request, user_id):
    if request.method !="GET":
        return Response(status=405, data="Can only do GET")
    print("here")
    followers = Follow.objects.filter(local_followee_id=user_id)  # Adjust this line based on your Follow model
    serializer = FollowSerializer(followers, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
def remove_follower(request, actor_id, object_id):
        # remove object_id for actor_id 
    return Response(status=200)

def decoder(foreign_author):
    pass

@api_view(['PUT'])
def add_follower(request, user_id, follower_id):

    # actor wants to follow object (object is local)
    if request.method !="PUT":
        return Response(status=405, data="Can only do PUT")


    # Get actor and object userID, check that it exists in the user database


    # make sure that actor and object are User models

    # Log the IDs and their types for debugging
    print(f"user_id: {user_id}, type: {type(user_id)}")
    print(f"follower_id: {follower_id}, type: {type(follower_id)}")

    try:
        # Query directly with string user_id
        user = User.objects.get(user_id=str(user_id))
        follower = User.objects.get(user_id=str(follower_id))

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    return Response(
        {"actor": follower.display_name, "object": user.display_name},
        status=200
    )
    # object = User.objects.get(user_id=user_id)
    # except:
    #     actor = None
    #     object = None
        
    # actor_host = None
    # if actor:
    #     actor_host = actor.host

    # actor_local = False
    # if actor_host.find('nodeaaaa')==1:
    #     actor_local = True

    # # Add it to the database
    # serializer = FollowSerializer()
    # serializer.add_follower(actor,actor_local,object)
    # return Response(status=200)

@api_view(['GET'])
def check_follower(request, actor_id, object_id):
    if request.method !="GET":
        return Response(status=405, data="Can only do GET")
   
    return Response(status=200)