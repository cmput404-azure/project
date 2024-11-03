
from datetime import datetime
from django.db import models
from .user import User
from .post import Post

class Share(models.Model):
    # user is the person who share
    # here we store all the user, post as URL because in case it is from remote, we can send to their endpoint to fetch data
    type = models.TextField(default="share", editable=False)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True) # always local
    user = models.URLField()
    post = models.URLField()
    created_at = models.DateTimeField("date reposted", default=datetime.now)
    