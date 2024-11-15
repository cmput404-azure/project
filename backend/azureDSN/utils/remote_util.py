import json
import http.client
from ..serializers.user_serializer import UserSerializer
from ..models import User
from urllib.parse import unquote, urlparse

def fetch_remote_user(remote_url):
    """
    Fetches remote follower data by sending a get request using the remote_url
    """
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
        parts = data.get("id").strip("/").split("/")

        userData={ 
            "id": parts[-1],
            "host": data.get("host"),
            "displayName": data.get("displayName"),
            "username": data.get("username"),
            "bio":data.get("bio"),
            "github": data.get("github"),
            "profile_image": data.get("profileImage"),
            "page": data.get("page")
            }
        serializer = UserSerializer(data = userData)
        if serializer.is_valid():
            user = User(**serializer.validated_data)  # Create an unsaved User instance
            return user
        else:
            print("Errors:", serializer.errors)
            return None
        
    except Exception as e:
        print(f"Error fetching remote follower {remote_url}: {str(e)}")
        return None