from urllib.parse import urlparse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from ..models import NodeUser, Follow
from requests.auth import HTTPBasicAuth
import requests, random, os


class RemoteAuthorsView(APIView):
    def get(self, request):
        """
            Fetch remote authors for recommended panel section.
        """
        try:
            all_remote_authors = []
            node_users = NodeUser.objects.all()

            for node in node_users:
                # We send our local credentials to the remote host
                authors = self.fetch_remote_authors(node.host, os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD'))
                all_remote_authors.extend(authors)

            random_authors = self.select_random_authors(all_remote_authors) if all_remote_authors else []
            
            return Response({"recommended_authors": random_authors}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
    def fetch_remote_authors(self, host, username, password, page=1, size=3):
        """
            Use BasicAuth to call remote endpoints with the given credentials.
        """
        try:
            parsed_url = urlparse(host)
            base_host = f"{parsed_url.scheme}://{parsed_url.netloc}"

            # Send a GET request to the remote node's authors endpoint
            response = requests.get(
                f"{base_host}/api/authors/",
                auth=HTTPBasicAuth(username, password),
                params={"page": page, "size": size},
                timeout=5
            )
            
            # Check if request was successful
            if response.status_code == 200:
                # Extract authors list from JSON response
                return response.json().get("authors", [])
            else:
                # This could mean the remote node does not grant us access to their data
                print(f"Failed to fetch authors from {host}: {response.status_code}")
                return []

        except requests.RequestException as e:
            print(f"Error fetching authors from {host}: {e}")
            return []
        
    def select_random_authors(self, authors, min_count=3, max_count=3):
        """
        Randomly select authors from a list.
        
        Args:
        - authors (list): List of author dictionaries.
        - min_count (int): Minimum number of authors to select.
        - max_count (int): Maximum number of authors to select.
        
        Returns:
        - list: List of randomly selected authors.
        """
        count = min(len(authors), random.randint(min_count, max_count))
        return random.sample(authors, count)
    
class RemoteFolloweeView(APIView):
    def get(self, request, local_serial, remote_fqid):
        """
            Checks if our local user with `local_serial` is following remote followee with `remote_fqid`
        """
        # Instead of calling remote server, we can check our Follow table
        follower = Follow.objects.filter(local_follower_id=local_serial, remote_followee__contains=remote_fqid)

        if follower:
            return Response({'is_follower': True}, status=200)
        else:
            return Response({'is_follower': False}, status=404)