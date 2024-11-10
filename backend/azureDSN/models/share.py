
from datetime import datetime
from django.db import models
from .user import User

class Share(models.Model):
    # user is the person who share
    # here we store all the user, post as URL because in case it is from remote, we can send to their endpoint to fetch data
    type = models.TextField(default="share", editable=False)
    # always local, we dont expect other team to call us anyway
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="receiver") # followers of user
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="sharer") # person shares the post
    post = models.URLField()
    created_at = models.DateTimeField("date reposted", default=datetime.now)
    