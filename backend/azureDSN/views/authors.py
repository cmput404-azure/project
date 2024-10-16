from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import User, Post
from ..serializers import UserSerializer, PostSerializer

class AuthorsView(APIView):
    def get(self, request, author_serial=None):
        """
        GET [local, remote] get the public authors
        """
        author = get_object_or_404(User, uuid=author_serial)
        print(author.display_name)
        serializer = UserSerializer(author)
        return Response(serializer.data, status=200)