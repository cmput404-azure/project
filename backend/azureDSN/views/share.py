from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import User, Post, Share
from ..serializers import ShareSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

class ShareView(APIView):
   
    def get(self, request):
        """
        gets all local posts and adds a 
        """
        shared_posts = Share.objects.all()
    
    def post(self, request, author_serial, post_fqid):
        post_id = post_fqid.split('/')[-1]
        post_obj = get_object_or_404(Post, uuid=post_id)        
        user_obj = get_object_or_404(User, uuid=author_serial)
        share_data = {
            "user": author_serial,
            "post":post_id
            }
        serializer = ShareSerializer(data=share_data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Shared successfully"}, status=200)
        else:
            return Response(serializer.errors, status=400)

