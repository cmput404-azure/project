from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from ..models import NodeUser, Follow
from ..utils import url_parser
from requests.auth import HTTPBasicAuth
import requests, random, os

@extend_schema(
    summary="Check Follow Status of Remote Followee.",
    description="Check if the local user with `local_serial` is following the remote user with `remote_fqid`.",
    parameters=[
        OpenApiParameter(
            name="local_serial",
            description="UUID of the local user whose following status we want to check.",
            type=str,
            required=True,
            location=OpenApiParameter.PATH
        ),
        OpenApiParameter(
            name="remote_fqid",
            description="Fully qualified ID (FQID) of the remote followee to check.",
            type=str,
            required=True,
            location=OpenApiParameter.PATH
        ),
    ],
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            description="The local user is following the remote followee.",
            response={
                "type": "object",
                "properties": {
                    "is_follower": {"type": "boolean", "example": True}
                }
            }
        ),
        status.HTTP_404_NOT_FOUND: OpenApiResponse(
            description="The local user is not following the remote followee.",
            response={
                "type": "object",
                "properties": {
                    "is_follower": {"type": "boolean", "example": False}
                }
            }
        ),
    },
    tags=["Remote API"]
)
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

@extend_schema(
    summary="Retrieve Remote Authors.",
    description="Fetch a list of remote authors from remote nodes listed in NodeUser, using basic authentication.",
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            description="A response containing a list of selected remote authors.",
            response={
                "type": "object",
                "properties": {
                    "type": {"type": "string", "example": "authors"},
                    "authors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string", "example": "author"},
                                "id": {"type": "string", "example": "http://nodeaaaa/api/authors/111"},
                                "host": {"type": "string", "example": "http://nodeaaaa/api/"},
                                "displayName": {"type": "string", "example": "Greg Johnson"},
                                "github": {"type": "string", "example": "http://github.com/gjohnson"},
                                "profileImage": {"type": "string", "example": "https://i.imgur.com/k7XVwpB.jpeg"},
                                "page": {"type": "string", "example": "http://nodeaaaa/authors/greg"}
                            }
                        }
                    }
                }
            }
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
            description="An error occurred while fetching remote authors."
        ),
    },
    tags=["Remote API"]
)
class RemoteAuthorsView(APIView):
    def get(self, request):
        """
            Fetch remote authors for recommended panel section.
        """
        if not request.user:
            return Response({"recommended_authors": []}, status=status.HTTP_200_OK)

        try:
            all_remote_authors = []
            node_users = NodeUser.objects.all()

            for node in node_users:
                # We send our local credentials to the remote host
                authors = self.fetch_remote_authors(node.host, os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD'))
                all_remote_authors.extend(authors)

            random_authors = self.select_random_authors(all_remote_authors, request.user.uuid) if all_remote_authors else []
            
            return Response({"recommended_authors": random_authors}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
    def fetch_remote_authors(self, host, username, password, page=1, size=3):
        """
            Use BasicAuth to call remote endpoints with the given credentials.
        """
        try:
            base_host = url_parser.get_base_host(host)

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
        
    def select_random_authors(self, authors, local_serial, min_count=5, max_count=5):
        """
        Randomly select authors from a list.
        
        Args:
        - authors (list): List of author dictionaries.
        - min_count (int): Minimum number of authors to select.
        - max_count (int): Maximum number of authors to select.
        
        Returns:
        - list: List of randomly selected authors.
        """

        def is_followed(author_id):
            """
            Check if the local user is already following the given author.
            
            Args:
            - author_id (str): The ID of the remote author.
            
            Returns:
            - bool: True if the author is followed, False otherwise.
            """
            response = RemoteFolloweeView().get(None, local_serial, author_id)
            return response.status_code == 200

        # Filter out authors already followed
        unfollowed_authors = [author for author in authors if not is_followed(author['id'])]
        count = min(len(unfollowed_authors), random.randint(min_count, max_count))
        
        # If there are fewer unfollowed authors than min_count, return all of them
        if len(unfollowed_authors) <= min_count:
            return unfollowed_authors

        # Otherwise, sample the desired number from unfollowed authors
        return random.sample(unfollowed_authors, count)
