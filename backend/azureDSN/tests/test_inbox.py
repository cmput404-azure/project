from unittest.mock import patch
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from ..models import User, Inbox, InboxItem, Post, FollowRequest, Share
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
import uuid
from rest_framework.response import Response
from ..views import InboxView


class InboxViewTestCase(TestCase):
    patch('azureDSN.utils.auth.TokenOrBasicAuthPermission.has_permission', return_value=True).start()
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.post = create_post(self.user)
        self.follower = create_user()
        # Set URL for the inbox, comment and post view
        self.inbox_url = reverse('inbox', kwargs={'author_serial': self.user.uuid}) 
        remote_uuid = uuid.uuid4()
        self.remote_inbox_url = f'http://localhost:8001/api/authors/{str(remote_uuid)}/inbox/'

    # Fetching empty inbox
    def test_get_with_empty_inbox(self):
        response = self.client.get(self.inbox_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["type"], "inbox")
        self.assertEqual(len(response.data["items"]), 0)
        
    # Test fetching no-exsit inbox (uuid doesn't exists)
    def test_get_nonexistent_inbox(self):
        nonexistent_inbox_url = "/api/authors/2677192c-bce3-4583-afe3-b6592155fe4c/inbox/"
        response = self.client.get(nonexistent_inbox_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
    def test_delete_follow_request(self):
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
        
    # Test delete no-exist type of inbox item   
    def test_delete_wrong_type(self):
        # Add follow request into inbox
        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        user_json = create_user_givenID(user_id=self.follower.uuid) # we store actor as json
        follow_obj = create_follow(user_json, self.user)
        create_inbox_item(follow_obj, inbox_obj)
        # Call to delete request
        payload = {
            "type": "abc",
            "id": 1
        }
        response = self.client.delete(self.inbox_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(inbox_obj.items.all()), 1) # Ensure inbox is empty

    # Send a DELETE request to delete a post
    def test_delete_local_post_from_local_user(self):
        # Add a post into inbox
        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        create_inbox_item(self.post, inbox_obj)
        payload = {
            "author": {
                "type": "author",
                "id": "http://localhost:8001/api/authors/e09c9fff-c5dc-4d9d-9fb1-667a564cd3dd",
                "bio": "",
                "displayName": "tino",
                "github": "https://github.com/QuinNguyen02",
                "host": "http://localhost:8001/api/",
                "profileImage": "",
                "username": "tino"
            },
            "comments": [],
            "content": "dfsfdsf",
            "contentType": "text/plain",
            "description": "dsfdfsdf",
            "follower": {
                "type": "author",
                "id": "http://localhost:8001/api/authors/a2d00814-ec38-4ea0-a297-7aa64b24a262",
                "host": "http://localhost:8001/api/"
            },
            "id": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
            "likes": [],
            "modified_at": "2024-11-17T02:17:33.067586Z",
            "published": "2024-11-17T02:17:33.022000Z",
            "title": "second post",
            "type": "post",
            "visibility": 3
        }
        
        response = self.client.delete(self.inbox_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(inbox_obj.items.all()), 1) # we delete existing one and add one with delete status
        self.assertEqual(inbox_obj.items.last().post_status, "delete")
        
    def test_delete_invalid_post_from_local_user(self):
        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        create_inbox_item(self.post, inbox_obj)
        # Define a payload with a non-existent post ID
        payload = {
            "author": {
                "type": "author",
                "id": "http://localhost:8001/api/authors/e09c9fff-c5dc-4d9d-9fb1-667a564cd3dd",
                "bio": "",
                "displayName": "tino",
                "github": "https://github.com/QuinNguyen02",
                "host": "http://localhost:8001/api/",
                "profileImage": "",
                "username": "tino"
            },
            "comments": [],
            "content": "dfsfdsf",
            "contentType": "text/plain",
            "description": "dsfdfsdf",
            "follower": {
                "type": "author",
                "id": "http://localhost:8001/api/authors/a2d00814-ec38-4ea0-a297-7aa64b24a262",
                "host": "http://localhost:8001/api/"
            },
            "id": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/2677192c-bce3-4583-afe3-b6592155fe4c",
            "likes": [],
            "modified_at": "2024-11-17T02:17:33.067586Z",
            "published": "2024-11-17T02:17:33.022000Z",
            "title": "second post",
            "type": "post",
            "visibility": 3
        }
        
        response = self.client.delete(self.inbox_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(inbox_obj.items.count(), 2) 
        self.assertEqual(inbox_obj.items.last().post_status, "delete")
        
    def test_delete_remote_post_from_local_user(self):
        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        
        # Define a payload with a post ID doesn't exist in Post model
        payload = {
            "author": {
                "type": "author",
                "id": "http://localhost:8001/api/authors/e09c9fff-c5dc-4d9d-9fb1-667a564cd3dd",
                "bio": "",
                "displayName": "tino",
                "github": "https://github.com/QuinNguyen02",
                "host": "http://localhost:8001/api/",
                "profileImage": "",
                "username": "tino"
            },
            "comments": [],
            "content": "dfsfdsf",
            "contentType": "text/plain",
            "description": "dsfdfsdf",
            "follower": {
                "type": "author",
                "id": "http://localhost:8001/api/authors/a2d00814-ec38-4ea0-a297-7aa64b24a262",
                "host": "http://localhost:8001/api/"
            },
            "id": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/2677192c-bce3-4583-afe3-b6592155fe4c",
            "likes": [],
            "modified_at": "2024-11-17T02:17:33.067586Z",
            "published": "2024-11-17T02:17:33.022000Z",
            "title": "second post",
            "type": "post",
            "visibility": 1    
        }
        
        create_inbox_remote_post(payload, inbox_obj) # add remote post into the inbox
        response = self.client.delete(self.inbox_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(inbox_obj.items.count(), 1) 
        self.assertIsNotNone(inbox_obj.items.last().remote_payload)
        self.assertEqual(inbox_obj.items.last().post_status, "delete")

    def test_delete_invalid_remote_post_from_local_user(self):
        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        
        # Define a payload with a post ID doesn't exist in Post model and Inbox model
        remote_payload = {
            "author": {
                "type": "author",
                "id": "http://localhost:8001/api/authors/e09c9fff-c5dc-4d9d-9fb1-667a564cd3dd",
                "bio": "",
                "displayName": "tino",
                "github": "https://github.com/QuinNguyen02",
                "host": "http://localhost:8001/api/",
                "profileImage": "",
                "username": "tino"
            },
            "comments": [],
            "content": "dfsfdsf",
            "contentType": "text/plain",
            "description": "dsfdfsdf",
            "follower": {
                "type": "author",
                "id": "http://localhost:8001/api/authors/a2d00814-ec38-4ea0-a297-7aa64b24a262",
                "host": "http://localhost:8001/api/"
            },
            "id": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/2677192c-bce3-4583-afe3-b6592155fe5d",
            "likes": [],
            "modified_at": "2024-11-17T02:17:33.067586Z",
            "published": "2024-11-17T02:17:33.022000Z",
            "title": "second post",
            "type": "post",
            "visibility": 1    
        }

        create_inbox_remote_post(remote_payload, inbox_obj) # add remote post into the inbox
        payload = {
            "author": {
                "type": "author",
                "id": "http://localhost:8001/api/authors/e09c9fff-c5dc-4d9d-9fb1-667a564cd3dd",
                "bio": "",
                "displayName": "tino",
                "github": "https://github.com/QuinNguyen02",
                "host": "http://localhost:8001/api/",
                "profileImage": "",
                "username": "tino"
            },
            "comments": [],
            "content": "dfsfdsf",
            "contentType": "text/plain",
            "description": "dsfdfsdf",
            "follower": {
                "type": "author",
                "id": "http://localhost:8001/api/authors/a2d00814-ec38-4ea0-a297-7aa64b24a262",
                "host": "http://localhost:8001/api/"
            },
            "id": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/2677192c-bce3-4583-afe3-b6592155fe6c",
            "likes": [],
            "modified_at": "2024-11-17T02:17:33.067586Z",
            "published": "2024-11-17T02:17:33.022000Z",
            "title": "second post",
            "type": "post",
            "visibility": 1    
        }
        response = self.client.delete(self.inbox_url, data=payload, format='json')
        
        self.assertEqual(inbox_obj.items.count(), 2) 
        self.assertIsNotNone(inbox_obj.items.last().remote_payload)
        self.assertIsNone(inbox_obj.items.first().post_status)
        self.assertEqual(inbox_obj.items.last().post_status,"delete")
    
    # Test update existing post 
    def test_update_local_post_from_local_user(self):
        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        # add post into inbox
        payload = {
            "author": {
                "type": "author",
                "id": "http://localhost:8001/api/authors/e09c9fff-c5dc-4d9d-9fb1-667a564cd3dd",
                "bio": "",
                "displayName": "tino",
                "github": "https://github.com/QuinNguyen02",
                "host": "http://localhost:8001/api/",
                "profileImage": "",
                "username": "tino"
            },
            "comments": [],
            "content": "dfsfdsf",
            "contentType": "text/plain",
            "description": "dsfdfsdf",
            "id": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
            "likes": [],
            "modified_at": "2024-11-17T02:17:33.067586Z",
            "published": "2024-11-17T02:17:33.022000Z",
            "title": "second post",
            "type": "post",
            "visibility": "PUBLIC"
        }
        response = self.client.post(self.inbox_url, data=payload, format='json')
        # try update post
        """Test updating an existing post in the inbox."""
        payload = {
            "author": {
                "type": "author",
                "id": "http://localhost:8001/api/authors/e09c9fff-c5dc-4d9d-9fb1-667a564cd3dd",
                "bio": "",
                "displayName": "tino",
                "github": "https://github.com/QuinNguyen02",
                "host": "http://localhost:8001/api/",
                "profileImage": "",
                "username": "tino"
            },
            "comments": [],
            "content": "dfsfdsf",
            "contentType": "text/plain",
            "description": "dsfdfsdf",
            "follower": {
                "type": "author",
                "id": "http://localhost:8001/api/authors/a2d00814-ec38-4ea0-a297-7aa64b24a262",
                "host": "http://localhost:8001/api/"
            },
            "id": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
            "likes": [],
            "modified_at": "2024-11-17T02:17:33.067586Z",
            "published": "2024-11-17T02:17:33.022000Z",
            "title": "This is the new title",
            "type": "post",
            "visibility": "PUBLIC"
        }
        response = self.client.put(self.inbox_url, data=payload, format='json')
        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "We have notified other users about your updated post")
        self.assertEqual(len(inbox_obj.items.all()), 2)
        self.assertEqual(inbox_obj.items.last().post_status, "update")
        self.assertEqual(inbox_obj.items.first().post_status, "edited")
        
    
    def test_update_remote_post_from_local_user(self):
        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        # add post into inbox
        payload = {
            "author": {
                "type": "author",
                "id": "http://localhost:8001/api/authors/e09c9fff-c5dc-4d9d-9fb1-667a564cd3dd",
                "bio": "",
                "displayName": "tino",
                "github": "https://github.com/QuinNguyen02",
                "host": "http://localhost:8001/api/",
                "profileImage": "",
                "username": "tino"
            },
            "comments": [],
            "content": "dfsfdsf",
            "contentType": "text/plain",
            "description": "dsfdfsdf",
            "id": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/e09c9fff-c5dc-4d9d-9fb1-667a564cd3dd",
            "likes": [],
            "modified_at": "2024-11-17T02:17:33.067586Z",
            "published": "2024-11-17T02:17:33.022000Z",
            "title": "second post",
            "type": "post",
            "visibility": 3
        }
        create_inbox_remote_post(payload, inbox_obj)
        # try update post
        """Test updating an existing post in the inbox."""
        payload = {
            "author": {
                "type": "author",
                "id": "http://localhost:8001/api/authors/e09c9fff-c5dc-4d9d-9fb1-667a564cd3dd",
                "bio": "",
                "displayName": "tino",
                "github": "https://github.com/QuinNguyen02",
                "host": "http://localhost:8001/api/",
                "profileImage": "",
                "username": "tino"
            },
            "comments": [],
            "content": "dfsfdsf",
            "contentType": "text/plain",
            "description": "dsfdfsdf",
            "follower": {
                "type": "author",
                "id": "http://localhost:8001/api/authors/a2d00814-ec38-4ea0-a297-7aa64b24a262",
                "host": "http://localhost:8001/api/"
            },
            "id": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/e09c9fff-c5dc-4d9d-9fb1-667a564cd3dd",
            "likes": [],
            "modified_at": "2024-11-17T02:17:33.067586Z",
            "published": "2024-11-17T02:17:33.022000Z",
            "title": "This is the new title",
            "type": "post",
            "visibility": 1
        }
        
        response = self.client.put(self.inbox_url, data=payload, format='json')
        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "We have notified other users about your updated post")
        self.assertEqual(len(inbox_obj.items.all()), 2)
        self.assertEqual(inbox_obj.items.last().post_status, "update")
        self.assertEqual(inbox_obj.items.first().post_status, "edited") 
        self.assertIsNotNone(inbox_obj.items.last().remote_payload)    
        self.assertIsNotNone(inbox_obj.items.first().remote_payload) 
        
    def test_invalid_type_for_update_post(self):
        # Add follow request into inbox
        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        # Call to update request
        payload = {
            "type": "abc",
            "id": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/e09c9fff-c5dc-4d9d-9fb1-667a564cd3dd",
            "likes": [],
            "modified_at": "2024-11-17T02:17:33.067586Z",
            "published": "2024-11-17T02:17:33.022000Z",
            "title": "This is the new title",
        }
        response = self.client.delete(self.inbox_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(inbox_obj.items.all()), 0) # Ensure inbox is empty
            
    
    # Test sending a post into one's inbox
    def test_post_invalid_inbox_obj(self):
        """Test creating a post in the inbox."""
        payload = {
            "type": "hihi",
            "id": f"{settings.BASE_URL}/api/authors/2677192c-bce3-4583-afe3-b6592155fe4c/posts/{self.post.uuid}",
            "description": "This post is a test",
            "contentType": "text/plain",
            "content": "Quin public a post, this notifies kyle's inbox",
            "comments": [],
            "likes": [],
            "visibility": 1,
        }

        response = self.client.post(self.inbox_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_post_missing_type(self):
        """Test creating a post in the inbox."""
        payload = {
            "id": f"{settings.BASE_URL}/api/authors/2677192c-bce3-4583-afe3-b6592155fe5a/posts/{self.post.uuid}",
            "description": "This post is a test",
            "contentType": "text/plain",
            "content": "Quin public a post, this notifies kyle's inbox",
            "comments": [],
            "likes": [],
            "visibility": 1,
            # "published": '2024-10-21T00:00:00Z',
        }

        response = self.client.post(self.inbox_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    # Test sending a follow request into one's inbox
    def test_create_follow_request(self):
        """Test creating a follow request in the inbox."""
        payload = {
            "type": "follow",
            "id": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/followers/{self.follower.uuid}",
            "actor":{
                "type":"author",
                "id":f"{settings.BASE_URL}/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                "host":f"{settings.BASE_URL}/azureDSN/",
                "displayName":"Quin Nguyen",
                "github": "https://github.com/QuinNguyen02",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
            },
            "object":{
                "type":"author",
                "id":f"{settings.BASE_URL}/api/authors/80ad41f4-7455-4771-a38a-2dedec3c1b00",
                "host":f"{settings.BASE_URL}/azureDSN/",
                "displayName":"Kyle Quach",
                "page":f"{settings.BASE_URL}/azureDSN/authors/kyle",
                "github": "https://github.com/KyleQuach03",
                "profileImage": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
            }
        }

        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        response = self.client.post(self.inbox_url, data=payload, format='json')
        self.assertEqual(len(inbox_obj.items.all()), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Follow request sent successfully")


    # Test sending a comment into one's inbox
    def test_create_comment(self):
        """Test creating a comment in the inbox."""
        payload = {
            "type": "comment",
            "post": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
            "author":{
                "type":"author",
                "id":f"{settings.BASE_URL}/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                "host":f"{settings.BASE_URL}/azureDSN/",
                "displayName":"Quin Nguyen",
                "github": "https://github.com/QuinNguyen02",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
            },
            "comment": "Nice post!",
        }

        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        response = self.client.post(self.inbox_url, data=payload, format='json')
        self.assertEqual(len(inbox_obj.items.all()), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Test sending a like into one's inbox
    def test_create_like(self):
        """Test creating a like in the inbox."""
        payload = {
            "type": "like",
            "object": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
            "author":{
                "type":"author",
                "id":f"{settings.BASE_URL}/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                "host":f"{settings.BASE_URL}/azureDSN/",
                "displayName":"Quin Nguyen",
                "github": "https://github.com/QuinNguyen02",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
            },
            "published": '2024-10-21T00:00:00Z'
        }

        response = self.client.post(self.inbox_url, data=payload, format='json')

        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(inbox_obj.items.all()), 1)
        self.assertEqual(response.data["message"], "Notified post's owner about your like successfully.")
        
    # Test sending a share into one's inbox
    def test_create_share(self):
        payload = {
            "type": "share",
            "sharer": f"{self.follower.uuid}",
            "post": f"{settings.BASE_URL}/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8e12/posts/82ae5a8c-02dd-4e47-a1e7-8d0d248f8e68"
        }
        response = self.client.post(self.inbox_url, data=payload, format='json')
        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(inbox_obj.items.all()), 1)
        try:
            share_obj = Share.objects.get(id=1)
            self.assertIsNotNone(share_obj) 
        except Share.DoesNotExist:
            self.assertRaises(ObjectDoesNotExist)

    # Tests that it is able to direct comments made on a remote post to the correct method
    @patch('azureDSN.views.inbox.InboxView.send_comment_to_remote')  
    def test_send_comment_to_remote(self, mock_send_comment):
        payload = {
            "type": "comment",
            "post": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
            "author":{
                "type":"author",
                "id":"http://localhost:8001/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                "host":"http://localhost:8001/azureDSN/",
                "displayName":"Quin Nguyen",
                "github": "https://github.com/QuinNguyen02",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
            },
            "comment": "Nice post!",
        }
        mock_send_comment.return_value = Response(200)

        response = self.client.post(self.remote_inbox_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Tests that it is able to build the correct url to send to the remote server
    def test_send_comment_to_remote_url(self):
        payload = {
            "type": "comment",
            "post": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
            "author":{
                "type":"author",
                "id":"http://localhost:8001/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                "host":"http://localhost:8001/azureDSN/",
                "displayName":"Quin Nguyen",
                "github": "https://github.com/QuinNguyen02",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
            },
            "comment": "Nice post!",
        }
        inbox_view = InboxView()

        response = inbox_view.send_comment_to_remote(payload=payload, request=f"http://testserver/api/authors/{self.user.uuid}/inbox/", test=True)
        self.assertEqual(response,f"{settings.BASE_URL}/api/authors/{self.user.uuid}/inbox/")

        # Tests that it is able to build the correct url to send to the remote server
    def test_send_comment_to_remote_no_author(self):
        payload = {
            "type": "comment",
            "post": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
            "comment": "Nice post!",
        }
        inbox_view = InboxView()

        response = inbox_view.send_comment_to_remote(payload=payload, request=f"http://testserver/api/authors/{self.user.uuid}/inbox/", test=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_comment_to_remote_invalid_author_id(self):
        payload = {
            "type": "comment",
            "post": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
            "author":{
                "type":"author",
                "id":"nope",
                "host":"http://localhost:8001/azureDSN/",
                "displayName":"Quin Nguyen",
                "github": "https://github.com/QuinNguyen02",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
            },
            "comment": "Nice post!",
        }
        inbox_view = InboxView()

        response = inbox_view.send_comment_to_remote(payload=payload, request=f"http://testserver/api/authors/{self.user.uuid}/inbox/", test=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_comment_to_remote_no_post(self):
        payload = {
            "type": "comment",
            "author":{
                "type":"author",
                "id":"http://localhost:8001/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                "host":"http://localhost:8001/azureDSN/",
                "displayName":"Quin Nguyen",
                "github": "https://github.com/QuinNguyen02",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
            },
            "comment": "Nice post!",
        }
        inbox_view = InboxView()

        response = inbox_view.send_comment_to_remote(payload=payload, request=f"http://testserver/api/authors/{self.user.uuid}/inbox/", test=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    # Tests that it is able to direct comments made on a remote post to the correct method
    @patch('azureDSN.views.inbox.InboxView.send_like_to_remote')  
    def test_send_like_to_remote(self, mock_send_like):
        payload = {
            "type": "like",
            "post": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
            "author":{
                "type":"author",
                "id":"http://localhost:8001/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                "host":"http://localhost:8001/azureDSN/",
                "displayName":"Quin Nguyen",
                "github": "https://github.com/QuinNguyen02",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
            },
            "published": '2024-10-21T00:00:00Z'

        }
        mock_send_like.return_value = Response(200)

        response = self.client.post(self.remote_inbox_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Tests that it is able to build the correct url to send to the remote server
    def test_send_like_to_remote_url(self):
            payload = {
                "type": "like",
                "object": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
                "author":{
                    "type":"author",
                    "id":"http://localhost:8001/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                    "host":"http://localhost:8001/azureDSN/",
                    "displayName":"Quin Nguyen",
                    "github": "https://github.com/QuinNguyen02",
                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                    "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
                },
                "authorId": f"{settings.BASE_URL}/api/authors/{self.user.uuid}"
            }
            inbox_view = InboxView()

            response = inbox_view.send_like_to_remote(payload=payload, request=None, test=True)

            self.assertEqual(response.status_code, 201)
    
    # Tests that malformed object fqids
    def test_send_like_to_remote_no_authorId(self):
        payload = {
                "type": "like",
                "object": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
                "author":{
                    "type":"author",
                    "id":"http://localhost:8001/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                    "host":"http://localhost:8001/azureDSN/",
                    "displayName":"Quin Nguyen",
                    "github": "https://github.com/QuinNguyen02",
                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                    "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
                },
            }
        
        inbox_view = InboxView()

        response = inbox_view.send_like_to_remote(payload=payload, request=None, test=True)
        self.assertEqual(response.status_code, 400)

    def test_send_like_to_remote_no_object(self):
        payload = {
                "type": "like",
                "author":{
                    "type":"author",
                    "id":"http://localhost:8001/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                    "host":"http://localhost:8001/azureDSN/",
                    "displayName":"Quin Nguyen",
                    "github": "https://github.com/QuinNguyen02",
                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                    "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
                },
                "authorId": f"{settings.BASE_URL}/api/authors/{self.user.uuid}"
            }
        
        inbox_view = InboxView()

        response = inbox_view.send_like_to_remote(payload=payload, request=None, test=True)
        self.assertEqual(response.status_code, 400)
    
    def test_send_like_to_remote_malformed_authorId(self):
        payload = {
                "type": "like",
                "object": f"{settings.BASE_URL}/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
                "author":{
                    "type":"author",
                    "id":"http://localhost:8001/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                    "host":"http://localhost:8001/azureDSN/",
                    "displayName":"Quin Nguyen",
                    "github": "https://github.com/QuinNguyen02",
                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                    "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
                },
                "authorId": "bad"
            }
        inbox_view = InboxView()
        response = inbox_view.send_like_to_remote(payload=payload, request=None, test=True)
        self.assertEqual(response.status_code, 400)

    def test_send_follow_request_to_remote_no_actor(self):
        payload = {
                "type": "follow",
                 "object":{
                    "type":"author",
                    "id":"http://nodebbbb/api/authors/222",
                    "host":"http://nodebbbb/api/",
                    "displayName":"Lara Croft",
                    "page":"http://nodebbbb/authors/222",
                    "github": "http://github.com/laracroft",
                    "profileImage": "http://nodebbbb/api/authors/222/posts/217/image"
                }
            }
        inbox_view = InboxView()
        response = inbox_view.send_follow_request_to_remote(payload=payload)
        self.assertEqual(response.status_code, 400)

    def test_send_follow_request_to_remote_invalid_actor_id(self):
        payload = {
                "type": "follow",
                "actor":{
                    "type":"author",
                    "id":"",
                    "host":"http://localhost:8001/azureDSN/",
                    "displayName":"Quin Nguyen",
                    "github": "https://github.com/QuinNguyen02",
                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                    "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
                },
                 "object":{
                    "type":"author",
                    "id":"http://nodebbbb/api/authors/222",
                    "host":"http://nodebbbb/api/",
                    "displayName":"Lara Croft",
                    "page":"http://nodebbbb/authors/222",
                    "github": "http://github.com/laracroft",
                    "profileImage": "http://nodebbbb/api/authors/222/posts/217/image"
                }
            }
        inbox_view = InboxView()
        response = inbox_view.send_follow_request_to_remote(payload=payload)
        self.assertEqual(response.status_code, 400)

    def test_send_follow_request_to_remote_no_object(self):
        payload = {
                "type": "follow",
                "actor":{
                    "type":"author",
                    "id":"http://localhost:8001/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                    "host":"http://localhost:8001/azureDSN/",
                    "displayName":"Quin Nguyen",
                    "github": "https://github.com/QuinNguyen02",
                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                    "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
                },
                
            }
        inbox_view = InboxView()
        response = inbox_view.send_follow_request_to_remote(payload=payload)
        self.assertEqual(response.status_code, 400)

    def test_send_follow_request_to_remote_invalid_object_id(self):
        payload = {
                "type": "follow",
                "actor":{
                    "type":"author",
                    "id":"",
                    "host":"http://localhost:8001/azureDSN/",
                    "displayName":"Quin Nguyen",
                    "github": "https://github.com/QuinNguyen02",
                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                    "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
                },
                 "object":{
                    "type":"author",
                    "id":"error",
                    "host":"http://nodebbbb/api/",
                    "displayName":"Lara Croft",
                    "page":"http://nodebbbb/authors/222",
                    "github": "http://github.com/laracroft",
                    "profileImage": "http://nodebbbb/api/authors/222/posts/217/image"
                }
            }
        inbox_view = InboxView()
        response = inbox_view.send_follow_request_to_remote(payload=payload)
        self.assertEqual(response.status_code, 400)
        
        

import random

def create_user():
    random_suffix = random.randint(1000, 9999)  # Add random digits to ensure uniqueness
    user_obj = User.objects.create(
                                    display_name=f"Test User{random_suffix}",
                                    username=f"Test User{random_suffix}",
                                    host=f"{settings.BASE_URL}/",
                                    github="http://github.com/testuser",
                                    page=f"{settings.BASE_URL}/authors/testuser",
                                    profile_image=None
                                )

    return user_obj
        
def create_post(user_obj):        
    post_obj = Post.objects.create(user=user_obj,
                                    title="Test Post",
                                    content="This is a test post",
                                    content_type="text/plain",
                                    visibility=1,
                                    has_image=False)
    return post_obj

def create_user_givenID(user_id):
    random_suffix = random.randint(1000, 9999) 
    user_obj = {
        "type": "author",
        "username": f"TestUser{random_suffix}",
        "id": f"{settings.BASE_URL}/authors/{user_id}",
        "url": f"{settings.BASE_URL}/authors/{user_id}",
        "host": f"{settings.BASE_URL}/",
        "displayName": f"TestUser{random_suffix}",
        "github": "http://github.com/quin",
        "profileImage": "http://testserver/profile"
    }
    return user_obj
    
def create_follow(actor, object):
    follow_obj = FollowRequest.objects.create(object=object, actor=actor)
    return follow_obj


def create_inbox_item(object, inbox_obj):
    content_type = ContentType.objects.get_for_model(object)
    id = getattr(object, 'uuid', getattr(object, 'id', None))
    inbox_item_obj = InboxItem.objects.create(content_type=content_type,
                                                 object_id=id,
                                                 content_object=object)
    inbox_obj.items.add(inbox_item_obj)

    return inbox_item_obj

def create_inbox_remote_post(remote_payload, inbox_obj, post_status=None):
    inbox_item_obj = InboxItem.objects.create(remote_payload=remote_payload, post_status=post_status)
    inbox_obj.items.add(inbox_item_obj)

    return inbox_item_obj
