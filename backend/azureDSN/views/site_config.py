from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import SiteConfiguration
from ..serializers import SiteConfigSerializer

class SiteConfigView(APIView):
    def get(self, request):
        config = SiteConfiguration.objects.first()
        serializer = SiteConfigSerializer(config)
        return Response(serializer.data)

    def put(self, request):
        config = SiteConfiguration.objects.first()
        serializer = SiteConfigSerializer(config, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)