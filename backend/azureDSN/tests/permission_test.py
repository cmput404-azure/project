from rest_framework.test import APIClient
from django.test import LiveServerTestCase
from django.conf import settings
from ..models import NodeUser, User
from requests.auth import HTTPBasicAuth
import os, requests

def construct_author_fqid(host, uuid):
    return f"{host}/authors/{uuid}"

class RemotePermissionsTest(LiveServerTestCase):
    def setUp(self):
        """
            Create a user and set up necessary variables.
        """
        self.client = APIClient()
        
        self.local_node = NodeUser.objects.create( # saved to remote database
            host=f"{settings.BASE_URL}",
            username=os.getenv("NODE_USERNAME"),
            password=os.getenv("NODE_PASSWORD"),
            is_authenticated=True
        )

        self.remote_author = User.objects.create_user( # To be stored in remote node
            display_name="Remote Author",
            username="remoteauthor",
            password="testpass",
            host=f"{self.live_server_url}/api/",
            github="http://github.com/remoteauthor",
            page=f"{self.live_server_url}/authors/remoteauthor",
            profile_image=None
        )

        self.internal_api_secret = settings.INTERNAL_API_SECRET
        
        self.author_url = f"{self.remote_author.host}authors/{self.remote_author.uuid}/"

    def test_successful_remote_connection(self):
        """
            Test a successful remote connection when remote node authorizes the local node.
        """
        response = requests.get(
                self.author_url,
                auth=HTTPBasicAuth(self.local_node.username, self.local_node.password),
            )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], f"{self.remote_author.host}authors/{self.remote_author.uuid}")
        self.assertEqual(response.json()['username'], self.remote_author.username)
        self.assertEqual(response.json()['displayName'], self.remote_author.display_name)
        self.assertEqual(response.json()['github'], self.remote_author.github)

    def test_failure_remote_connection_invalid_credentials(self):
        response = requests.get(
                self.author_url,
                auth=HTTPBasicAuth(self.local_node.username, "wrong password"),
            )
        
        # This should return 403 because the credentials sent and saved in remote DB is not equal
        self.assertEqual(response.status_code, 403)

        response = requests.get(
                self.author_url,
                auth=HTTPBasicAuth("wrong username", self.local_node.password),
            )
        
        self.assertEqual(response.status_code, 403)

    def test_failure_remote_connection_no_header_sent(self):
        response = requests.get(
            self.author_url,
            # No header
        )

        self.assertEqual(response.status_code, 403)

    def test_failure_remote_connection_unauthorized(self):
        self.local_node.is_authenticated = False
        self.local_node.save() # Remote node will not respond to requests from local node

        response = requests.get( # Credentials are correct, we just don't have access
            self.author_url,
            auth=HTTPBasicAuth(self.local_node.username, self.local_node.password)
        )

        self.assertEqual(response.status_code, 403)

    def test_send_remote_follow_request(self):
        self.local_follower = User.objects.create(
            host=f"{settings.BASE_URL}/api/",
            username="local",
            password="localpass",
            display_name="Local Follower",
            bio="I'm a test user",
            profile_image=None,
            github="https://github.com/login",
            page=f"{settings.BASE_URL}/authors/local"
        )

        # Pretend local user does something that triggers this through the frontend
        payload = {
            "type": "follow",
            "summary": f"{self.local_follower.username} wants to follow {self.remote_author.username}",
            "actor": {
                "type": "author",
                "id": f"{construct_author_fqid(self.local_follower.host, self.local_follower.uuid)}",
                "host": f"{self.local_follower.host}",
                "displayName": f"{self.local_follower.display_name}",
                "username": f"{self.local_follower.username}",
                "bio": f"{self.local_follower.bio}",
                "profileImage": f"{self.local_follower.profile_image}",
                "github": f"{self.local_follower.github}",
                "page": f"{self.local_follower.page}",
            },
            "object": {
                "type": "author",
                "id": f"{construct_author_fqid(self.remote_author.host, self.remote_author.uuid)}",
                "host": f"{self.remote_author.host}",
                "displayName": f"{self.remote_author.display_name}",
                "username": f"{self.remote_author.username}",
                "bio": f"{self.remote_author.bio}",
                "profileImage": f"{self.remote_author.profile_image}",
                "github": f"{self.remote_author.github}",
                "page": f"{self.remote_author.page}",
            }
        }

        response = requests.post( # Sending a follow request to remote node
            f"{self.remote_author.host}authors/{self.remote_author.uuid}/inbox",
            json=payload,
            auth=HTTPBasicAuth(self.local_node.username, self.local_node.password)
        )

        self.assertEqual(response.status_code, 200)

