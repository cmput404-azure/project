from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from ..models import Share, User

class ShareViewTests(APITestCase):
    patch('azureDSN.utils.auth.TokenOrBasicAuthPermission.has_permission', return_value=True).start()
    def setUp(self):
        self.client = APIClient()
        # Set up a test user and test data for posts
        self.user = User.objects.create(
            display_name="Test User",
            username="Test User",
            host="http://localhost:8000/api/",
            github="https://github.com/testuser",
            page="http://localhost:8000/authors/testuser",
            profile_image=None
        )
        self.user2 = User.objects.create(
            display_name="Test User2",
            username="Test User2",
            host="http://localhost:8000/api/",
            github="https://github.com/testuser2",
            page="http://localhost:8000/authors/testuser2",
            profile_image=None
        )
        self.share_url = reverse('shared', kwargs={'author_serial': self.user.uuid}) 
        self.valid_post_fqid = "http://127.0.0.1:8000/api/authors/12345678-1234-5678-1234-567812345678/posts/87654321-4321-8765-4321-876543218765"
        self.invalid_post_fqid = "http://127.0.0.1:8000/api/authors/invalid_uuid/posts/invalid_uuid"

    def test_get_share_exists(self):
        # Set up a share for the user
        Share.objects.create(user=self.user, post=self.valid_post_fqid, type="share")

        # Perform GET request to check if share exists
        response = self.client.get(self.share_url, {'post_fqid': self.valid_post_fqid})

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['exists'], True)

    def test_get_share_does_not_exist(self):
        # Perform GET request with a post that hasn't been shared
        response = self.client.get(self.share_url, {'post_fqid': self.valid_post_fqid})

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['exists'], False)

    def test_get_share_missing_post_fqid(self):
        # Perform GET request without post_fqid
        response = self.client.get(self.share_url)

        # Check the response for missing post_fqid parameter
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("post_fqid is a required query parameter.", response.data['error'])

    def test_post_add_share_successfully(self):
        # Perform POST request to add a share
        data = {'post': self.valid_post_fqid}
        response = self.client.post(self.share_url, data, format='json')

        # Check if share was created successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Store share successfully")
        self.assertTrue(Share.objects.filter(user=self.user, post=self.valid_post_fqid).exists())

    def test_post_add_share_missing_post(self):
        # Perform POST request without 'post' in data
        response = self.client.post(self.share_url, {}, format='json')

        # Check the response for missing post field
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("post is a required field.", response.data['error'])

    def test_post_add_share_invalid_post_url(self):
        # Perform POST request with an invalid post URL
        data = {'post': "invalid_url"}
        response = self.client.post(self.share_url, data, format='json')

        # Check if the response returns an error for the invalid URL
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Enter a valid URL.", response.data['post'][0])

    def test_post_add_share_with_nonexistent_user(self):
        # Perform POST request with a nonexistent user UUID
        non_existent_uuid = "00000000-0000-0000-0000-000000000000"
        url = reverse('shared', kwargs={'author_serial': non_existent_uuid}) 
        data = {'post': self.valid_post_fqid}
        response = self.client.post(url, data, format='json')

        # Check if the response returns a 404 error for nonexistent user
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_share_with_nonexistent_user(self):
        # Perform GET request with a nonexistent user UUID
        non_existent_uuid = "00000000-0000-0000-0000-000000000000"
        url = reverse('shared', kwargs={'author_serial': non_existent_uuid}) 
        response = self.client.get(url, {'post_fqid': self.valid_post_fqid})

        # Check if the response returns a 404 error for nonexistent user
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_add_duplicate_share(self):
        # Set up an initial share for the user
        Share.objects.create(user=self.user, post=self.valid_post_fqid, type="share")

        # Perform POST request to add the same share again
        data = {'post': self.valid_post_fqid}
        response = self.client.post(self.share_url, data, format='json')

        # Check if duplicate shares are prevented or handled
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Share.objects.filter(user=self.user, post=self.valid_post_fqid).count(), 1)