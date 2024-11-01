from datetime import datetime
from django.db import models
from .user import User
from .post import Post

class Share(models.Model):
    # user is the reposter, it is local
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField("date reposted", default=datetime.now)

