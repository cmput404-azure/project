from django.db import models
from datetime import datetime
from .user import User
from .inbox_item import InboxItem


class Inbox(models.Model):
    # Each user will have her/his own inbox which basically stores all types of items: post, follow, comment and like
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(InboxItem)