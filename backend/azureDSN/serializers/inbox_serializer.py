from rest_framework import serializers
from rest_framework.serializers import *

from ..models import InboxItem, Inbox
from .inbox_item_serializer import InboxItemSerializer
from ..utils.serializer_utils import create_url_from_uuid

'''
Using ModelSerializer instead of Serializer so that the set of fields are automatically generated based on the model
It also includes the simple default implementation of .create() and .update()
https://www.geeksforgeeks.org/modelserializer-in-serializers-django-rest-framework/
SerializerMethodField is used to personalize the function to serialize the chosen field
'''
class InboxSerializer(serializers.ModelSerializer):
    user = SerializerMethodField("get_user_id")
    items = SerializerMethodField("get_items")
    type = SerializerMethodField("get_type")

    class Meta:
        model = Inbox
        fields = ["user", "items", "type"]

    # This should return the user id in format of their url
    def get_user_id(self, obj):
        return create_url_from_uuid(obj=obj, request=self.context["request"], source="inbox") 

    # This create the InboxItem matching the 
    def get_items(self, obj):
        return InboxItemSerializer(obj.items.all().order_by("id"), many=True, context=self.context).data

    def get_type(self, obj):
        return "inbox"
