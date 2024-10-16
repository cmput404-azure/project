from rest_framework import serializers
from .user_serializer import UserSerializer
from ..models import Follow
from ..models import FollowRequest
class FollowSerializer(serializers.ModelSerializer):
    # actor = UserSerializer()
    # object = UserSerializer()

    # Example:
    # summary: "Greg follows Lara"
    # actor: user object Greg
    # object: user object Lara
    def add_follower(self, actor,actor_local, object,):
        # probably don't need to check for object_local
        if (actor_local==True):
            return Follow(local_followee = actor, local_follower=object)
        elif(actor_local==False):
            return Follow(local_followee = actor, remote_follower=object)



    class Meta:
        fields = ('summary', 'actor', 'object')
