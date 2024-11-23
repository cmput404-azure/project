from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from ..models import Follow, User
from urllib.parse import quote
from django.conf import settings
from unittest.mock import patch
import uuid

class FollowTests(APITestCase):
    def setUp(self):
        patch('azureDSN.utils.auth.TokenOrBasicAuthPermission.has_permission', return_value=True).start()
        self.user1_data = {
            "display_name": "TestUser1",
            "username":"TestUser1",
            "github": "https://github.com/login",
            "host": f"{settings.BASE_URL}/api/",
            "page": f"{settings.BASE_URL}/authors/1",
            "profile_image":"profile_pictures/seabackground.jpg"
        }
        self.user2_data = {
            "display_name": "TestUser2",
            "username":"TestUser2",
            "github": "https://github.com/login",
            "host": f"{settings.BASE_URL}/api/",
            "page": f"{settings.BASE_URL}/authors/2",
            "profile_image":"profile_pictures/seabackground.jpg"
        }
        self.user3_data = {
            "display_name": "TestUser3",
            "username":"TestUser3",
            "github": "https://github.com/login",
            "host": f"{settings.BASE_URL}/api/",
            "page": f"{settings.BASE_URL}/authors/3",
            "profile_image":"profile_pictures/seabackground.jpg"
        }

        """Set up test data for the API calls."""

        self.user1 = User.objects.create(**self.user1_data)
        self.user2 = User.objects.create(**self.user2_data)
        self.user3 = User.objects.create(**self.user3_data)
        # Create follow relationships
        Follow.objects.create(local_follower_id=self.user1.uuid, local_followee_id=self.user2.uuid)
        Follow.objects.create(local_follower_id=self.user2.uuid, local_followee_id=self.user1.uuid)

        # Set up the API client
        self.client = APIClient()

    def test_get_following(self):
        """Test retrieving users that the current user is following."""
        url = reverse('following', args=[self.user1.uuid])  
        response = self.client.get(f"{url}?action=following")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["followers"]), 1)
        self.assertEqual(response.data["followers"][0]["displayName"], "TestUser2")

    def test_get_friends(self):
        """Test retrieving mutual friends."""
        url = reverse('following', args=[self.user1.uuid])  
        response = self.client.get(f"{url}?action=friends")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Expecting 1 mutual friend
        self.assertEqual(response.data[0]["displayName"], "TestUser2")

    def test_no_friends(self):
        """Test case where a user has no mutual friends."""
        url = reverse('following', args=[self.user3.uuid])
        response = self.client.get(f"{url}?action=friends")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) 

    def test_no_following(self):
        url = reverse('following', args=[self.user3.uuid])
        response = self.client.get(f"{url}?action=friends")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) 
    
    def test_get_follower(self):
        url = reverse('get_followers', args=[self.user2.uuid])  
        response = self.client.get(f"{url}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["followers"]), 1)
        self.assertEqual(response.data["followers"][0]["displayName"], "TestUser1")

    def test_get_no_follower(self):
        url = reverse('get_followers', args=[self.user3.uuid])  
        response = self.client.get(f"{url}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["followers"]), 0)
    
    def test_get_non_existing_follower(self):
        '''
        If follower not avail in local, we try to find in remote and if given host param is not provided => neither remote nor local
        '''
        random_uuid = uuid.uuid4()
        url = reverse('get_followers', args=[random_uuid])  
        response = self.client.get(f"{url}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_follower(self):
        follower_url = f'{settings.BASE_URL}/api/authors/{self.user3.uuid}'
        encoded_url = quote(follower_url, safe="")
        url = reverse('followers_handler', args=[self.user2.uuid, encoded_url])  
        response = self.client.put(f"{url}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # check that followers table updated 
        url_follower = reverse('get_followers', args = [self.user2.uuid])
        follower_response = self.client.get(f"{url_follower}")
        self.assertEqual(follower_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(follower_response.data["followers"]), 2)

    def test_add_existing_follower(self):
        follower_url = f'{settings.BASE_URL}/api/authors/{self.user2.uuid}'
        encoded_url = quote(follower_url, safe="")
        url = reverse('followers_handler', args=[self.user1.uuid, encoded_url])  
        response = self.client.put(f"{url}")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        
        # check that followers table updated 
        url_follower = reverse('get_followers', args = [self.user1.uuid])
        follower_response = self.client.get(f"{url_follower}")
        self.assertEqual(follower_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(follower_response.data["followers"]), 1)

    def test_delete_follower(self):
        follower_url = f'{settings.BASE_URL}/api/authors/{self.user2.uuid}'
        encoded_url = quote(follower_url, safe="")
        url = reverse('followers_handler', args=[self.user1.uuid, encoded_url])  
        response = self.client.delete(f"{url}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # check that followers table updated 
        url_follower = reverse('get_followers', args = [self.user1.uuid])
        follower_response = self.client.get(f"{url_follower}")
        self.assertEqual(follower_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(follower_response.data["followers"]), 0)

    def test_delete_non_existing_follower(self):
        follower_url = f'{settings.BASE_URL}/api/authors/{self.user3.uuid}'
        encoded_url = quote(follower_url, safe="")
        url = reverse('followers_handler', args=[self.user1.uuid, encoded_url])  
        response = self.client.delete(f"{url}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_check_follower(self):
        follower_url = f'{settings.BASE_URL}/api/authors/{self.user2.uuid}'
        encoded_url = quote(follower_url, safe="")
        url = reverse('followers_handler', args=[self.user1.uuid, encoded_url])  
        response = self.client.get(f"{url}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_no_follower(self):
        follower_url = f'{settings.BASE_URL}/api/authors/{self.user3.uuid}'
        encoded_url = quote(follower_url, safe="")
        url = reverse('followers_handler', args=[self.user1.uuid, encoded_url])  
        response = self.client.get(f"{url}")
        self.assertEqual(response.data["is_follower"], False)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)