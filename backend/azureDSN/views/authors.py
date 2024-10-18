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
    
    def put(self, request, author_serial=None):
        """
        PUT [local]: update a particular author's profile
        """

        print("Received request data:", request.data)
        author = get_object_or_404(User, uuid=author_serial)
        serializer = UserSerializer(author, data=request.data) # Send the whole JSON object everytime so partial won't be True

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)
    
class AuthorsCompleteView(APIView):
    def get(self,request):
        authors = User.objects.all()
        serializer = UserSerializer(authors, many=True)
        return Response(serializer.data)
