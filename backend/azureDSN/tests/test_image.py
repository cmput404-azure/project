from unittest.mock import patch
from django.conf import settings
from rest_framework.test import APITestCase, APIClient
from ..models import User, Post
from django.urls import reverse
from rest_framework import status
import uuid

class ImageAPITest(APITestCase):
    patch('azureDSN.utils.auth.TokenOrBasicAuthPermission.has_permission', return_value=True).start()
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            display_name="Test User",
            username="Test User",
            host=f"{settings.BASE_URL}/api/",
            github="http://github.com/testuser",
            page=f"{settings.BASE_URL}/authors/testuser",
            profile_image=None
        )

        self.post = Post.objects.create(
            title="A post with image",
            content="iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==",
            has_image=True,
            content_type="image/png;base64",
            user=self.user
        )

    def test_get_image_binary_by_serial(self):
        # Test successful response, should return the data url and MIME type of the image
        url = reverse('get_image_by_serial', kwargs={
            'author_serial': self.user.uuid,
            'post_serial': self.post.uuid
        })

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data, f"data:{self.post.content_type},{self.post.content}")

    def test_invalid_serials(self):
        # Test invalid author serial and invalid post serial, should return 404
        url = reverse('get_image_by_serial', kwargs={
            'author_serial': uuid.uuid4(),
            'post_serial': self.post.uuid
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = reverse('get_image_by_serial', kwargs={
            'author_serial': self.user.uuid,
            'post_serial': uuid.uuid4()
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_image_binary_by_fqid(self):
        # Test get image data url by post fqid
        url = reverse('get_image_by_fqid', kwargs={
            'post_fqid': f"{self.user.host}authors/{self.user.uuid}/posts/{self.post.uuid}/"
        })

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data, f"data:{self.post.content_type},{self.post.content}")

    def test_invalid_fqid(self):
        # Test error state using invalid post uuid that invalidates the fqid
        url = reverse('get_image_by_fqid', kwargs={
            'post_fqid': f"{self.user.host}authors/{self.user.uuid}/posts/not-a-valid-uuid/"
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)