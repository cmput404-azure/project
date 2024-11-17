from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import SiteConfiguration
from ..serializers import SiteConfigSerializer

class SiteConfigView(APIView):

    @extend_schema(
        summary="Retrieve site configuration.",
        description="Fetches the current site configuration, specifically the registration approval setting.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="Successful response",
                response=SiteConfigSerializer,
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Configuration not found",
                response={ "type": "object", "properties": { "error": { "type": "string", "example": "Configuration not found" }}}
            ),
        },
    )
    def get(self, request):
        config = SiteConfiguration.objects.first()
        serializer = SiteConfigSerializer(config)
        return Response(serializer.data)


    @extend_schema(
        summary="Update site configuration.",
        description="Updates the site configuration to toggle the requirement for admin approval after registration.",
        request=SiteConfigSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="Configuration updated successfully.",
                response=SiteConfigSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid data or validation errors.",
                response={ "type": "object", "properties": { "error": { "type": "string", "example": "Invalid data" }}}
            ),
        },
    )
    def put(self, request):
        config = SiteConfiguration.objects.first()
        serializer = SiteConfigSerializer(config, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)