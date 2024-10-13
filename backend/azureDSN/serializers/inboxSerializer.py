from rest_framework import serializers
from rest_framework.serializers import *

from ..models import Inbox

class InboxSerializer(serializers.ModelSerializer):
    user = SerializerMethodField("getUserURL")
    items = SerializerMethodField("getItems")
    type = SerializerMethodField("getType")

    class Meta:
        model = Inbox
        fields = ("type", "user", "items")

    def getUserURL(self, obj):
        return build_default_author_uri(obj=obj, request=self.context["request"], source = "inbox")

    def getItems(self, obj):
        return InboxItemSerializer(obj.items.all().order_by("-id"), many=True, context=self.context).data

    def getType(self, obj):
        return "inbox"