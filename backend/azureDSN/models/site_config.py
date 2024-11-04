from django.db import models

class SiteConfiguration(models.Model):
    require_approval = models.BooleanField(default=True)