from drf_spectacular.utils import OpenApiExample
from rest_framework import serializers
from ..models import SiteConfiguration

class SiteConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteConfiguration
        fields = ['require_approval']
        examples = [
            OpenApiExample(
                name="Site Configuration Example",
                value={
                    "require_approval": True
                }
            )
        ]