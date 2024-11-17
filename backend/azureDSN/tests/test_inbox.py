from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from ..models import User, Inbox, InboxItem, Post, FollowRequest, Share
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

class InboxViewTestCase(TestCase):
    patch('azureDSN.utils.auth.TokenOrBasicAuthPermission.has_permission', return_value=True).start()
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
            "id": f"http://localhost:8000/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
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
            "id": f"http://localhost:8000/api/authors/{self.user.uuid}/posts/2677192c-bce3-4583-afe3-b6592155fe4c",
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
            "id": f"http://localhost:8000/api/authors/{self.user.uuid}/posts/2677192c-bce3-4583-afe3-b6592155fe4c",
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
            "id": f"http://localhost:8000/api/authors/{self.user.uuid}/posts/2677192c-bce3-4583-afe3-b6592155fe5d",
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
            "id": f"http://localhost:8000/api/authors/{self.user.uuid}/posts/2677192c-bce3-4583-afe3-b6592155fe6c",
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
            "id": f"http://localhost:8000/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
            "likes": [],
            "modified_at": "2024-11-17T02:17:33.067586Z",
            "published": "2024-11-17T02:17:33.022000Z",
            "title": "second post",
            "type": "post",
            "visibility": 3
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
            "id": f"http://localhost:8000/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
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
        self.assertEqual(response.data["message"], "We have noticed other users about your updated post")
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
            "id": f"http://localhost:8000/api/authors/{self.user.uuid}/posts/e09c9fff-c5dc-4d9d-9fb1-667a564cd3dd",
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
            "id": f"http://localhost:8000/api/authors/{self.user.uuid}/posts/e09c9fff-c5dc-4d9d-9fb1-667a564cd3dd",
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
        self.assertEqual(response.data["message"], "We have noticed other users about your updated post")
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
            "id": f"http://localhost:8000/api/authors/{self.user.uuid}/posts/e09c9fff-c5dc-4d9d-9fb1-667a564cd3dd",
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
            "id": f"http://localhost:8000/api/authors/2677192c-bce3-4583-afe3-b6592155fe4c/posts/{self.post.uuid}",
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
            "id": f"http://localhost:8000/api/authors/2677192c-bce3-4583-afe3-b6592155fe5a/posts/{self.post.uuid}",
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

        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        response = self.client.post(self.inbox_url, data=payload, format='json')
        self.assertEqual(len(inbox_obj.items.all()), 1)
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
            "comment": "Nice post!",
        }

        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        response = self.client.post(self.inbox_url, data=payload, format='json')
        self.assertEqual(len(inbox_obj.items.all()), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test sending a like into one's inbox
    def test_create_like(self):
        """Test creating a like in the inbox."""
        payload = {
            "type": "like",
            "object": f"http://localhost:8000/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
            "author":{
                "type":"author",
                "id":"http://127.0.0.1:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8ee0",
                "host":"http://127.0.0.1:8000/azureDSN/",
                "displayName":"Quin Nguyen",
                "github": "https://github.com/QuinNguyen02",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "page": "profile_pictures/Screenshot_2024-10-17_014549_YLob4WX.png"
            },
            "published": '2024-10-21T00:00:00Z'
        }

        response = self.client.post(self.inbox_url, data=payload, format='json')

        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(inbox_obj.items.all()), 1)
        self.assertEqual(response.data["message"], "Notice post's owner about your like successfully")
        
    # Test sending a share into one's inbox
    def test_create_share(self):
        payload = {
            "type": "share",
            "sharer": f"{self.follower.uuid}",
            "post": "http://localhost:8000/api/authors/82ae5a8c-02dd-4e47-a1e7-8d0d248f8e12/posts/82ae5a8c-02dd-4e47-a1e7-8d0d248f8e68"
        }
        response = self.client.post(self.inbox_url, data=payload, format='json')
        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(inbox_obj.items.all()), 1)
        try:
            share_obj = Share.objects.get(id=1)
            self.assertIsNotNone(share_obj) 
        except Share.DoesNotExist:
            self.assertRaises(ObjectDoesNotExist)
        
        

import random

def create_user():
    random_suffix = random.randint(1000, 9999)  # Add random digits to ensure uniqueness
    user_obj = User.objects.create(
                                    display_name=f"Test User{random_suffix}",
                                    username=f"Test User{random_suffix}",
                                    host="http://localhost:8000/",
                                    github="http://github.com/testuser",
                                    page="http://localhost:8000/authors/testuser",
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
        "id": f"http://127.0.0.1:8000/authors/{user_id}",
        "url": f"http://127.0.0.1:8000/authors/{user_id}",
        "host": "http://127.0.0.1:8000/",
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
    inbox_item_object = InboxItem.objects.create(remote_payload=remote_payload, post_status=post_status)
    inbox_obj.items.add(inbox_item_object)
