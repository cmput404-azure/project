from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from ..models import User, Inbox, InboxItem, Post, FollowRequest, Comment, Like
from urllib.parse import urlparse
from ..utils.test_util import *


class InboxViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.post = create_post(self.user)
        self.follower = create_user()
        # Set URL for the inbox, comment and post view
        self.inbox_url = reverse('inbox', kwargs={'author_serial': self.user.uuid})

    
    # Fetching empty inbox
    def test_get_with_empty_inbox(self):
        response = self.client.get(self.inbox_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["type"], "inbox")
        self.assertEqual(len(response.data["items"]), 0)
        
    # Check fetching all items in the inbox
    def test_get_inbox_items(self):
        # Add follow request into inbox
        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        user_json = create_user_givenID(user_id=self.follower.uuid) # we store actor as json
        follow_obj = create_follow(user_json, self.user)
        create_inbox_item(follow_obj, inbox_obj)
        response = self.client.get(self.inbox_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["items"][0]["type"], "follow")
        self.assertEqual(response.data['type'], 'inbox')

    # Send a DELETE request to delete follow request
    def test_delete_inbox(self):
        # Add follow request into inbox
        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        user_json = create_user_givenID(user_id=self.follower.uuid) # we store actor as json
        follow_obj = create_follow(user_json, self.user)
        create_inbox_item(follow_obj, inbox_obj)
        # Call to delete request
        payload = {
            "type": "follow",
            "id": 1
        }
        response = self.client.delete(self.inbox_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(inbox_obj.items.all()), 0) # Ensure inbox is empty

    # Send a DELETE request to delete a post
    def test_delete_post(self):
        # Add a post into inbox
        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        create_inbox_item(self.post, inbox_obj)
        payload = {
            "type": "post",
            "id": f"http://localhost:8000/api/authors/{self.user.uuid}/posts/{self.post.uuid}"
        }
        
        response = self.client.delete(self.inbox_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(len(inbox_obj.items.all()), 0)

    # Test sending a post into one's inbox
    def test_create_post(self):
        """Test creating a post in the inbox."""
        payload = {
            "type": "post",
            "id": f"http://localhost:8000/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
            "description": "This post is a test",
            "contentType": "text/plain",
            "content": "Quin public a post, this notifies kyle's inbox",
            "author":{
                "type":"test author",
                "id":f"http://localhost:8000/api/authors/{self.user.uuid}",
                "host":"http://127.0.0.1:8000/azureDSN/",
                "displayName":"Test User",
                "github": "https://github.com/QuinNguyen02",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "page": "post_images/Screenshot_2024-10-17_014549.png"
            },
            "comments": {},
            "likes": {},
            "published": "2024-10-19T13:07:04+00:00",
            "visibility": 1,
        }

        response = self.client.post(self.inbox_url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "We have noticed other users about your post")


    # Test sending a follow request into one's inbox
    def test_create_follow_request(self):
        """Test creating a follow request in the inbox."""
        payload = {
            "type": "follow",
            "id": f"http://localhost:8000/api/authors/{self.user.uuid}/followers/{self.follower.uuid}",
            "actor":{
                "type":"author",
                "id":"http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                "host":"http://127.0.0.1:8000/azureDSN/",
                "displayName":"Quin Nguyen",
                "github": "https://github.com/QuinNguyen02",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
            },
            "object":{
                "type":"author",
                "id":"http://127.0.0.1:8000/api/authors/80ad41f4-7455-4771-a38a-2dedec3c1b00",
                "host":"http://127.0.0.1:8000/azureDSN/",
                "displayName":"Kyle Quach",
                "page":"http://127.0.0.1:8000/azureDSN/authors/kyle",
                "github": "https://github.com/KyleQuach03",
                "profileImage": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
            }
        }

        response = self.client.post(self.inbox_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Follow request sent successfully")


    # Test sending a comment into one's inbox
    def test_create_comment(self):
        """Test creating a comment in the inbox."""
        payload = {
            "type": "comment",
            "post": f"http://localhost:8000/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
            "author":{
                "type":"author",
                "id":"http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                "host":"http://127.0.0.1:8000/azureDSN/",
                "displayName":"Quin Nguyen",
                "github": "https://github.com/QuinNguyen02",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
            },
            "published": "2024-10-19T12:00:00Z",
            "comment": "Nice post!",
            "contentType": "text/plain"
        }

        response = self.client.post(self.inbox_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Notice post's owner about your comment successfully")

    # Test sending a like into one's inbox
    def test_create_like(self):
        """Test creating a like in the inbox."""
        payload = {
            "type": "like",
            "object": f"http://localhost:8000/api/authors/{self.user.uuid}/liked/{self.post.uuid}",
            "author":{
                "type":"author",
                "id":"http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                "host":"http://127.0.0.1:8000/azureDSN/",
                "displayName":"Quin Nguyen",
                "github": "https://github.com/QuinNguyen02",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
            },
            "published": "2024-10-19T12:00:00Z"
        }

        response = self.client.post(self.inbox_url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Notice post's owner about your like successfully")
