from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from datetime import datetime


'''
An inbox can receive different data types like follow, like, comment and post. ContentType can be a representation of any models
in our project. Using it will allow the inbox to store a generic type of one of the four models listed above flexibly
Reference: https://docs.djangoproject.com/en/5.1/ref/contrib/contenttypes/ 
Date: 12/10/2024
'''
class InboxItem(models.Model):
    '''
    content_type is a reference to a model instance whose id is object_id and actual object is content_object
    remote_payload is the JSON data sent with the request yet don't match any models, this usually causes by the object
    being sent belongs to a remote user ~ not in our database
    '''
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    remote_payload = models.JSONField(null=True, blank=True)
    time = models.DateTimeField(default=datetime.now)
    post_status = models.CharField(default=None, blank=True, null=True, max_length=10)
    
