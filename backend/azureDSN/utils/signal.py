from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import User, Inbox

'''
This function automatically create an inbox for every new user added into the db
From nidhi1408 - 3 years ago
https://www.reddit.com/r/django/comments/rlar20/django_do_something_only_when_model_instance/
'''
@receiver(post_save, sender=User)
def create_inbox(sender, instance, created, **kwargs):
    if created:
        Inbox.objects.create(user=instance)
