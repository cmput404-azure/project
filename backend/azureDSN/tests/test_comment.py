import uuid
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from ..models import Comment, Post, User
from unittest.mock import patch
class CommentsAPITest(APITestCase):
    patch('azureDSN.utils.auth.TokenOrBasicAuthPermission.has_permission', return_value=True).start()
    def setUp(self):
        self.client = APIClient()
        
        # Set up a user and post for testing comments
        self.user = User.objects.create(
            display_name="Test User",
            username="testuser",
            host="http://localhost:8000/api/",
            github="https://github.com/testuser",
            page="http://localhost:8000/authors/testuser",
            profile_image=None
        )

        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post.",
            user=self.user
        )

        # Create a comment on the post
        self.comment = Comment.objects.create(
            comment="This is a test comment.",
            post=self.post,
            user={
                "type": "author",
                "id": str(self.user.uuid),
                "host": self.user.host,
                "displayName": self.user.display_name,
                "github": self.user.github,
                "page": self.user.page,
            },
            contentType="text/plain"
        )

    def test_get_multiple_comments_by_author_and_post_serial(self):
        # Retrieve comments by author and post serial
        url = reverse('comments_by_serial', kwargs={
            'author_serial': self.user.uuid,
            'post_serial': self.post.uuid
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], "comments")
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['src']), 1)
        self.assertEqual(response.data['src'][0]['comment'], "This is a test comment.")
        self.assertEqual(response.data['src'][0]['author']['displayName'], self.user.display_name)

    def test_get_multiple_comments_invalid_author_or_post_serial(self):
        # Test invalid author serial
        url = reverse('comments_by_serial', kwargs={
            'author_serial': uuid.uuid4(),
            'post_serial': self.post.uuid
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test invalid post serial
        url = reverse('comments_by_serial', kwargs={
            'author_serial': self.user.uuid,
            'post_serial': uuid.uuid4()
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_single_comment_by_serials(self):
        # Retrieve a single comment by author, post, and comment serials
        url = reverse('comment_by_serial', kwargs={
            'author_serial': self.user.uuid,
            'post_serial': self.post.uuid,
            'comment_serial': self.comment.uuid
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], "This is a test comment.")
        self.assertEqual(response.data['post'], f"{self.user.host}authors/{self.user.uuid}/posts/{self.post.uuid}")

    def test_get_single_comment_invalid_serial(self):
        # Test invalid comment serial
        url = reverse('comment_by_serial', kwargs={
            'author_serial': self.user.uuid,
            'post_serial': self.post.uuid,
            'comment_serial': uuid.uuid4()
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_multiple_comments_by_post_fqid(self):
        # Retrieve multiple comments using post FQID
        url = reverse('comments_by_fqid', kwargs={
            'post_fqid': f"{self.user.host}api/posts/{self.post.uuid}"
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], "comments")
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['src']), 1)
        self.assertEqual(response.data['src'][0]['comment'], "This is a test comment.")
        self.assertEqual(response.data['src'][0]['author']['displayName'], self.user.display_name)

    def test_get_multiple_comments_invalid_post_fqid(self):
        # Test invalid post FQID
        url = reverse('comments_by_fqid', kwargs={
            'post_fqid': f"{self.user.host}api/posts/invalid-uuid"
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_single_comment_by_fqid(self):
        # Retrieve a single comment using comment FQID
        url = reverse('comment_by_fqid', kwargs={
            'comment_fqid': f"{self.user.host}api/comments/{self.comment.uuid}"
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], "This is a test comment.")

    def test_get_single_comment_invalid_fqid(self):
        # Test invalid comment FQID
        url = reverse('comment_by_fqid', kwargs={
            'comment_fqid': f"{self.user.host}api/comments/invalid-uuid"
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)