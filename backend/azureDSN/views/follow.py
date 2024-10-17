import json
from django.http import Http404, HttpResponse, HttpResponseRedirect
from rest_framework.views import APIView
import http.client
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..serializers.follow_serializer import FollowSerializer
from ..serializers.user_serializer import UserSerializer
from ..models import Follow
from ..models import User
from urllib.parse import quote, unquote, urlparse

def fetch_remote_follower_data(remote_url):
    """Fetch remote follower data using HTTP GET."""
    try:
        # Parse the remote URL to get the host and path
        parsed_url = urlparse(remote_url)

        if not parsed_url.path.endswith('/'):
            parsed_url = parsed_url._replace(path=parsed_url.path + '/')
        connection = http.client.HTTPConnection(parsed_url.netloc)

        # Perform the GET request
        connection.request("GET", parsed_url.path)
        response = connection.getresponse()
        data = json.loads(response.read().decode())
        return {
            "uuid": data.get("id"),
            "host": data.get("host"),
            "display_name": data.get("displayName"),
            "github": data.get("github"),
            "profileImage": data.get("profileImage"),
            "page": data.get("page"),
        }
    except Exception as e:
        print(f"Error fetching remote follower {remote_url}: {str(e)}")
        return None
        
class FollowGetView(APIView): 
    def get(request, user_id):
        # Get the followers list from Follow model
        followers = Follow.objects.filter(local_followee_id=user_id) 
        followerSerializer = FollowSerializer(followers, many=True)
        print(followerSerializer.data)
        combined_followers = []

        for follower in followers:
            if follower.remote_follower:  # Remote follower handling
                remote_data = fetch_remote_follower_data(follower.remote_follower)
                if remote_data:
                    combined_followers.append(remote_data)
            else:  # Local follower handling
                try:
                    user = User.objects.get(uuid=follower.local_follower_id)
                    combined_followers.append(user)
                except User.DoesNotExist:
                    raise Http404(f"Local follower with ID {follower.local_follower_id} not found.")


        # Using the remote_follower_id and local_follower_id, use the GET user endpoint
        serializer = UserSerializer(combined_followers, many=True)

        response_data = {
        "type": "followers",
        "followers": serializer.data,
        }
        return Response(response_data)
    
class FollowChangeView(APIView):        
    http_method_names = ['get', 'put', 'delete']  # Allow only these methods

    def get(self, request, user_id, follower_url):
        """Handle GET request to check if the user is a follower."""
        return self.get_followers(request, user_id)

    def put(self, request, user_id, follower_url):
        """Handle PUT request to add a follower."""
        return self.add_follower(request, user_id, follower_url)

    def delete(self, request, user_id, follower_url):
        """Handle DELETE request to remove a follower."""
        return self.remove_follower(request, user_id, follower_url)

    def remove_follower(self, request, user_id, follower_url):
        # remote follower
        follower = Follow.objects.filter(local_followee_id = user_id, remote_follower=follower_url)

        # local follower
        if not follower:
            decoded_url = unquote(follower_url)
            parts = decoded_url.strip("/").split("/")
            follower_id = parts[-1]
            follower = Follow.objects.filter(local_followee_id = user_id, local_follower_id=follower_id)
        
        follower.delete()
        return Response({"message": "Follower removed successfully"}, status=204)

    
    def add_follower(self,request, user_id, follower_url):  
        decoded_url = unquote(follower_url)
        parts = decoded_url.strip("/").split("/")
        follower_host = f"{parts[0]}//{parts[2]}"  # Extract scheme and host (e.g., http://127.0.0.1:8000)
        follower_id = parts[-1]
        try:
            user = User.objects.get(uuid=user_id)
           
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        

        follower_local = False
        if follower_host.find('127.0.0.1')!=-1:
            follower_local = True

        follow_data = {
            "local_followee": user_id,
            "remote_followee": None,
            "local_follower": follower_id if follower_local else None,
            "remote_follower": decoded_url if not follower_local else None,
        }
        serializer = FollowSerializer(data=follow_data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Follower added successfully"}, status=200)
        else:
            return Response(serializer.errors, status=400)

    def check_follower(self,request, user_id, follower_url):
        # remote follower
        follower = Follow.objects.filter(local_followee_id = user_id, remote_follower=follower_url)

        # local follower
        if not follower:
            decoded_url = unquote(follower_url)
            parts = decoded_url.strip("/").split("/")
            follower_id = parts[-1]
            follower = Follow.objects.filter(local_followee_id = user_id, local_follower_id=follower_id)
        

        if not follower:  # neither local nor remote
            return Response(status=404)
        else:
            return Response(status=200)