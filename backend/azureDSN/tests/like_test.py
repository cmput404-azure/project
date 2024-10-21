import uuid
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from ..models import Like, Post, User

class LikesAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            display_name="Test User",
            username="Test User",
            host="http://localhost:8000/",
            github="http://github.com/testuser",
            page="http://localhost:8000/authors/testuser",
            profile_image=None
        )

        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post.",
            user=self.user,
            image=None
        )

        self.like = Like.objects.create(
            user={
                "type": self.user.type,
                "id": str(self.user.uuid),
                "host": self.user.host,
                "displayName": self.user.display_name,
                "github": self.user.github,
                "page": self.user.page,
            },
            post=self.post
        )

    def test_get_like_by_author_serial_and_like_serial(self):
        url = reverse('get_like_by_serial', kwargs={
            'author_serial': self.user.uuid,
            'like_serial': self.like.uuid
        })

        # Send a GET request to the LikeView
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response data
        self.assertEqual(response.data['type'], f"like")
        self.assertEqual(response.data['author']["displayName"], f"{self.user.display_name}")
        self.assertEqual(response.data['id'], f"http://testserver/api/authors/{self.user.uuid}/liked/{self.like.uuid}")
        self.assertEqual(response.data['object'], f"http://testserver/api/authors/{self.user.uuid}/posts/{self.post.uuid}")

    def test_get_like_invalid_serial(self):
        # Invalid author_serial
        url = reverse('get_like_by_serial', kwargs={
            'author_serial': uuid.uuid4(),
            'like_serial': self.like.uuid
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # invalid like_serial
        url = reverse('get_like_by_serial', kwargs={
            'author_serial': self.user.uuid,
            'like_serial': uuid.uuid4()
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_like_by_like_fqid(self):
        url = reverse('get_like_by_fqid', kwargs={
            'like_fqid': f"http://{self.user.host}api/like/{self.like.uuid}"
        })

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['type'], f"like")
        self.assertEqual(response.data['author']["displayName"], f"{self.user.display_name}")
        self.assertEqual(response.data['id'], f"http://testserver/api/authors/{self.user.uuid}/liked/{self.like.uuid}")
        self.assertEqual(response.data['object'], f"http://testserver/api/authors/{self.user.uuid}/posts/{self.post.uuid}")

    def test_get_like_invalid_fqid(self):
        url = reverse('get_like_by_fqid', kwargs={
            'like_fqid': f"http://{self.user.host}api/like/not-a-uuid"
        })

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_author_likes_by_serial(self):
        url = reverse('author_likes_by_serial', kwargs={
            'author_serial': self.user.uuid
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['type'], f"likes")
        self.assertEqual(response.data['id'], f"http://testserver/api/authors/{self.user.uuid}/liked/")
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['src']), 1)
        self.assertEqual(response.data['src'][0]['author']['id'], f"{self.user.uuid}")

    def test_get_author_likes_invalid_serial(self):
        url = reverse('author_likes_by_serial', kwargs={
            'author_serial': uuid.uuid4()
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_author_likes_fqid(self):
        url = reverse('author_likes_by_fqid', kwargs={
            'author_fqid': f"{self.user.host}api/author/{self.user.uuid}"
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['type'], f"likes")
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['src']), 1)
        self.assertEqual(response.data['src'][0]['author']['id'], f"{self.user.uuid}")

    def test_get_author_likes_invalid_fqid(self):
        url = reverse('author_likes_by_fqid', kwargs={
            'author_fqid': f"{self.user.host}api/author/not-a-valid-uuid"
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_post_likes_by_serial(self):
        url = reverse('get_likes_by_serial', kwargs={
            'author_serial': self.user.uuid,
            'post_serial': self.post.uuid
        })

        # Make another user like the post as well
        self.user2 = User.objects.create(
            display_name="Test User 2",
            host="http://localhost:8000/",
            github="http://github.com/testuser2",
            page="http://localhost:8000/authors/testuser2",
            profile_image=None
        )

        self.like = Like.objects.create(
            user= {
                "type": self.user2.type,
                "id": str(self.user2.uuid),
                "host": self.user2.host,
                "displayName": self.user2.display_name,
                "github": self.user2.github,
                "page": self.user2.page,
            },
            post= self.post
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['type'], f"likes")
        self.assertEqual(response.data['id'], f"http://testserver/api/authors/{self.user.uuid}/posts/{self.post.uuid}/likes/")
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['src']), 2)
        self.assertEqual(response.data['src'][0]['author']['id'], f"{self.user2.uuid}") # the latest one is on top

    def test_get_post_likes_invalid_serial(self):
        url = reverse('get_likes_by_serial', kwargs={
            'author_serial': uuid.uuid4(),
            'post_serial': self.post.uuid
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = reverse('get_likes_by_serial', kwargs={
            'author_serial': self.user.uuid,
            'post_serial': uuid.uuid4()
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_post_likes_by_fqid(self):
        url = reverse('get_likes_by_fqid', kwargs={
            'post_fqid': f"{self.user.host}api/posts/{self.post.uuid}"
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['type'], f"likes")
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['src']), 1)
        self.assertEqual(response.data['src'][0]['author']['id'], f"{self.user.uuid}")

    def test_get_post_likes_invalid_fqid(self):
        url = reverse('get_likes_by_fqid', kwargs={
            'post_fqid': f"{self.user.host}api/author/"
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



