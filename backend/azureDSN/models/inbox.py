from django.db import models
from datetime import datetime
from .user import User
from .inboxItem import InboxItem


class Inbox(models.Model):
    # Each user will have her/his own inbox which basically stores all types of items: post, follow, comment and like
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(InboxItem)