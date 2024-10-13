from rest_framework import serializers
from rest_framework.serializers import *

from ..models import *
from .serializers import InboxItemSeriallizer

class InboxSerializer(serializers.ModelSerializer):
    user = SerializerMethodField("getUserURL")
    items = SerializerMethodField("getItems")
    type = SerializerMethodField("getType")

    class Meta:
        model = Inbox
        fields = ("type", "user", "items")

    def getUserURL(self, obj):
        # get user id in form of url
        pass

    def getItems(self, obj):
        # get the InboxItem object
        pass

    def getType(self, obj):
        return "inbox"