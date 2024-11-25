import uuid
from django.db import models
from datetime import datetime
from .post import Post


class Comment(models.Model):
    type = models.TextField(default="comment", editable=False)
    user = models.JSONField(default=dict, db_column="user") # can be local or remote
    comment = models.CharField(max_length=500)
    contentType = models.TextField(default='text/plain')
    created_at = models.DateTimeField("date commented", default=datetime.now)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)  # The ID of comment 
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null = True, blank = True)
    remote_post = models.URLField(blank=True, null=True)