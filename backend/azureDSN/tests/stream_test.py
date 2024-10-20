from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from ..models import Post, User

class StreamViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            display_name="Test User",
            host="http://localhost:8000/",
            github="http://github.com/testuser",
            page="http://localhost:8000/authors/testuser",
            profile_image=None
        )
        # self.client.force_authenticate(user=self.user)

        self.post = Post.objects.create(
            title="Test Post 1",
            content="This is a test post 1.",
            user=self.user,
            image=None,
            visibility=1
        )

        self.post2 = Post.objects.create(
            title="Test Post 2",
            content="This is a test post 2.",
            user=self.user,
            image=None,
            visibility=1
        )

        self.post3 = Post.objects.create(
            title="Test Post 3",
            content="This is a deleted post.",
            user=self.user,
            image=None,
            visibility=4
        )

    def test_stream_view(self):
        url = reverse('stream')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
