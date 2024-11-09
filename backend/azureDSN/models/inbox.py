from django.db import models
from .user import User
from .inbox_item import InboxItem


class Inbox(models.Model):
    # Each user will have her/his own inbox which basically stores all types of items: post, follow, comment and like
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(InboxItem)

    def __str__(self):
        """String representation for the inbox object (useful for admin panels)."""
        return f"{self.user}'s Inbox)"