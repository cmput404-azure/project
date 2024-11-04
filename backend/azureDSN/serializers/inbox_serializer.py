from rest_framework import serializers
from rest_framework.serializers import *
from ..models import *
from .inbox_item_serializer import InboxItemSerializer
from ..utils.serializer_util import create_url_from_uuid

'''
Using ModelSerializer instead of Serializer so that the set of fields are automatically generated based on the model
It also includes the simple default implementation of .create() and .update()
https://www.geeksforgeeks.org/modelserializer-in-serializers-django-rest-framework/
SerializerMethodField is used to personalize the function to serialize the chosen field
'''
class InboxSerializer(serializers.ModelSerializer):
    user = SerializerMethodField("get_user_id_in_url")
    items = SerializerMethodField("get_items")
    type = SerializerMethodField("get_type")

    class Meta:
        model = Inbox
        fields = ["user", "items", "type"]

    # This should return the user id in format of their url
    def get_user_id_in_url(self, obj):
        return create_url_from_uuid(obj=obj, request=self.context["request"], type="inbox") 

    # Order the items in descending order of id because we are trying to get the latest inbox item 
    def get_items(self, obj):
        return InboxItemSerializer(obj.items.all().order_by("-id"), many=True, context=self.context).data

    def get_type(self, obj):
        return "inbox"
