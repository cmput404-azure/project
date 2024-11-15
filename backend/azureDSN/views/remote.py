from urllib.parse import urlparse
from ..models.user import NodeUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from requests.auth import HTTPBasicAuth
import requests, random

class RemoteAuthorsView(APIView):
    def get(self, request):
        """
            Fetch remote authors for recommended panel section.
        """
        try:
            all_remote_authors = []
            node_users = NodeUser.objects.all()

            for node in node_users:
                if node.is_authenticated:
                    authors = self.fetch_remote_authors(node.host, node.username, node.password)
                    all_remote_authors.extend(authors)

            random_authors = self.select_random_authors(all_remote_authors)
            print(f"Selected authors: {random_authors}")
            
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