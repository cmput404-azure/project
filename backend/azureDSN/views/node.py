
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from ..models.user import NodeUser

class NodeUserView(APIView):
    def get(self, request):
        """
            Fetch the list of `NodeUser` table.
        """
        
        # We only want to display these in the frontend
        node_users = NodeUser.objects.values('host', 'username', 'password', 'is_authenticated')

        # List of dictionaries automatically converted into JSON by DRF
        return Response(node_users, status=status.HTTP_200_OK)