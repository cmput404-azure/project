from unittest.mock import patch
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from ..models import Post, User, Follow

class StreamViewTest(APITestCase):
    patch('azureDSN.utils.auth.TokenOrBasicAuthPermission.has_permission', return_value=True).start()
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            display_name="Test User",
            username="testuser",
            password="azure404",
            host="http://localhost:8000/",
            github="http://github.com/testuser",
            page="http://localhost:8000/authors/testuser",
            profile_image=None
        ) # originally unauthenticated

        self.friend_user = User.objects.create_user(
            display_name="Friend User",
            username="frienduser",
            password="azure404",
            host="http://localhost:8000/",
            github="http://github.com/frienduser",
            page="http://localhost:8000/authors/frienduser",
            profile_image=None
        )

        self.friend_user_2 = User.objects.create_user(
            display_name="Friend User 2",
            username="frienduser2",
            password="azure404",
            host="http://localhost:8000/",
            github="http://github.com/frienduser2",
            page="http://localhost:8000/authors/frienduser2",
            profile_image=None
        )

        self.post_public = Post.objects.create(
            title="Test Post 1",
            content="This is a public test post 1.",
            user=self.user,
            visibility=1
        )

        self.post_public = Post.objects.create(
            title="Test Post 2",
            content="This is a public test post 2.",
            user=self.user,
            visibility=1
        )

        self.post_friends_only = Post.objects.create(
            title="My Friends Only Post",
            content="This is a friends-only post.",
            user=self.user,
            visibility=2 
        )

        self.post_unlisted = Post.objects.create(
            title="My Unlisted Post",
            content="This is an unlisted post.",
            user=self.user,
            visibility=3
        )

        self.post_deleted = Post.objects.create(
            title="Test Post 3",
            content="This is a deleted post.",
            user=self.user,
            visibility=4
        )

        self.other_post_public = Post.objects.create(
            title="Other Public Post",
            content="This is a public post of another user.",
            user=self.friend_user,
            visibility=1
        )

        self.other_post_friends_only = Post.objects.create(
            title="Other Friends Only Post",
            content="This is a friends-only post of another user.",
            user=self.friend_user,
            visibility=2 
        )

        self.other_post_unlisted = Post.objects.create(
            title="Other Unlisted Post",
            content="This is an unlisted post of another user.",
            user=self.friend_user,
            visibility=3
        )

    def test_public_stream_view(self): # Public stream for both auth and unauth user
        url = reverse('stream')
        response = self.client.get(url)

        returned_posts = response.data["src"]
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(returned_posts), 3) # deleted, friends-only and unlisted posts not shown in public stream
        
        # Check sorting order (Newest post at top)
        self.assertEqual(returned_posts[0]['title'], "Other Public Post") # created last
        self.assertEqual(returned_posts[1]['title'], "Test Post 2")
        self.assertEqual(returned_posts[2]['title'], "Test Post 1")

    def test_auth_stream_view(self):
        url = reverse('auth_stream')

        # Authenticate the client
        self.client.force_authenticate(user=self.user)

        response = self.client.get(url)

        returned_posts = response.data["src"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(returned_posts), 2) # My friends-only and unlisted post, other user should not show up here because I'm not following them yet
        self.assertEqual(returned_posts[0]['title'], "My Unlisted Post")
        self.assertEqual(returned_posts[1]['title'], "My Friends Only Post")

    def test_follow_auth_stream_view(self):
        Follow.objects.create(local_follower_id=self.user.uuid, local_followee_id=self.friend_user.uuid)

        url = reverse('auth_stream')

        # Authenticate the client
        self.client.force_authenticate(user=self.user)

        response = self.client.get(url)

        returned_posts = response.data["src"]

        self.assertEqual(response.status_code, 200)

        # User is now following another user, their unlisted post should show up
        self.assertEqual(len(returned_posts), 3) # Friends-only is not shown here yet because the relationship is one-way
        
        self.assertEqual(returned_posts[0]['title'], "Other Unlisted Post")
        self.assertEqual(returned_posts[1]['title'], "My Unlisted Post")
        self.assertEqual(returned_posts[2]['title'], "My Friends Only Post")

    def test_friends_auth_stream_view(self):
        # Create Friend relationship
        Follow.objects.create(local_follower_id=self.user.uuid, local_followee_id=self.friend_user.uuid)
        Follow.objects.create(local_follower_id=self.friend_user.uuid, local_followee_id=self.user.uuid)
        
        url = reverse('auth_stream')

        self.client.force_authenticate(user=self.user)

        response = self.client.get(url)

        returned_posts = response.data["src"]

        self.assertEqual(response.status_code, 200)

        # User should be able to see unlisted and friends-only post of people they are following and friends with        
        self.assertEqual(len(returned_posts), 4)

        self.assertEqual(returned_posts[0]['title'], "Other Unlisted Post")
        self.assertEqual(returned_posts[1]['title'], "Other Friends Only Post")
        self.assertEqual(returned_posts[2]['title'], "My Unlisted Post")
        self.assertEqual(returned_posts[3]['title'], "My Friends Only Post")

    def test_unauthenticated_auth_stream_view(self):
        url = reverse('auth_stream')
        response = self.client.get(url)

        returned_posts = response.data["src"]
        
        # In the frontend, you can't view the auth stream because the button is hidden, so instead of returning error code, it returns empty array
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(returned_posts), 0) # empty, because user is unauthenticated, can't fetch non-public posts as that is specific to user