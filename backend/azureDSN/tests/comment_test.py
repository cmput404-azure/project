# azureDSN/tests/test_comments.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from ..models import User, Post, Comment
import uuid

class MultipleCommentsViewTest(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create(
            display_name="Test User",
            username="testuser",
            host="http://localhost:8000/",
            github="http://github.com/testuser",
            page="http://localhost:8000/authors/testuser"
        )

        # Create a post
        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post.",
            user=self.user
        )

        # Create comments
        self.comments = []
        for i in range(15):
            comment = Comment.objects.create(
                post=self.post,
                user={
                    "type": "author",
                    "id": str(self.user.uuid),
                    "host": self.user.host,
                    "displayName": self.user.display_name,
                    "github": self.user.github,
                    "page": self.user.page,
                },
                comment=f"Comment {i + 1}",
                contentType="text/plain",
                created_at=timezone.now()
            )
            self.comments.append(comment)

    def test_get_comments_by_author_and_post_serial(self):
        url = reverse('comments_by_serial', kwargs={
            'author_serial': self.user.uuid,
            'post_serial': self.post.uuid
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'comments')
        self.assertEqual(response.data['count'], 15)
        self.assertEqual(len(response.data['src']), 10)  # Limited to 10
        self.assertEqual(response.data['id'], f"http://testserver/api/authors/{self.user.uuid}/posts/{self.post.uuid}/comments")
        self.assertEqual(response.data['page'], f"http://testserver/api/authors/{self.user.uuid}/posts/{self.post.uuid}")











    # def test_get_comments_by_post_fqid(self):
    #     post_fqid = f"http://localhost:8000/api/authors/{self.user.uuid}/posts/{self.post.uuid}"
    #     url = reverse('comments_by_fqid', kwargs={'post_fqid': post_fqid})
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['type'], 'comments')
    #     self.assertEqual(response.data['count'], 15)
    #     self.assertEqual(len(response.data['src']), 10)

    # # def test_get_comments_invalid_author_serial(self):
    # #     invalid_author_uuid = uuid.uuid4()
    # #     url = reverse('comments_by_serial', kwargs={
    # #         'author_serial': invalid_author_uuid,
    # #         'post_serial': self.post.uuid
    # #     })
    # #     response = self.client.get(url)
    # #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_get_comments_invalid_post_fqid(self):
    #     invalid_post_fqid = 'invalid-fqid'
    #     url = reverse('comments_by_fqid', kwargs={'post_fqid': invalid_post_fqid})
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# class SingleCommentViewTest(APITestCase):
#     def setUp(self):
#         # Create a user
#         self.user = User.objects.create(
#             display_name="Test User",
#             username="testuser",
#             host="http://localhost:8000/",
#             github="http://github.com/testuser",
#             page="http://localhost:8000/authors/testuser"
#         )

#         # Create a post
#         self.post = Post.objects.create(
#             title="Test Post",
#             content="This is a test post.",
#             user=self.user
#         )

#         # Create a comment
#         self.comment = Comment.objects.create(
#             post=self.post,
#             user={
#                 "type": "author",
#                 "id": str(self.user.uuid),
#                 "host": self.user.host,
#                 "displayName": self.user.display_name,
#                 "github": self.user.github,
#                 "page": self.user.page,
#             },
#             comment="This is a test comment.",
#             contentType="text/plain",
#             created_at=timezone.now()
#         )

#     def test_get_comment_by_serial(self):
#         url = reverse('comment_by_serial', kwargs={
#             'author_serial': self.user.uuid,
#             'post_serial': self.post.uuid,
#             'comment_serial': self.comment.uuid
#         })
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['comment'], self.comment.comment)
#         self.assertEqual(response.data['id'], self.comment.get_id())  # Assuming get_id() method

#     def test_get_comment_by_fqid(self):
#         comment_fqid = f"http://localhost:8000/api/comments/{self.comment.uuid}"
#         url = reverse('comment_by_fqid', kwargs={'comment_fqid': comment_fqid})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['comment'], self.comment.comment)
#         self.assertEqual(response.data['id'], self.comment.get_id())

#     def test_get_comment_invalid_serial(self):
#         invalid_comment_uuid = uuid.uuid4()
#         url = reverse('comment_by_serial', kwargs={
#             'author_serial': self.user.uuid,
#             'post_serial': self.post.uuid,
#             'comment_serial': invalid_comment_uuid
#         })
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#     def test_get_comment_invalid_fqid(self):
#         invalid_comment_fqid = 'invalid-fqid'
#         url = reverse('comment_by_fqid', kwargs={'comment_fqid': invalid_comment_fqid})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
