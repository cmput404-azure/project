from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from ..models import User, Inbox, InboxItem, Post, FollowRequest
from django.contrib.contenttypes.models import ContentType

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
        self.assertEqual(len(inbox_obj.items.all()), 0) # Ensure inbox is empty

    # Test update existing post 
    def test_update_existing_post(self):
        # add post into inbox
        payload = {
            "type": "post",
            "id": f"http://localhost:8000/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
            "description": "This post is a test",
            "contentType": "text/plain",
            "content": "This is a test post",
            "title": "Test Post",
            "published": "2024-10-19T13:07:04+00:00",
            "visibility": 1,
        }

        response = self.client.post(self.inbox_url, data=payload, format='json')
        # try update post
        """Test updating an existing post in the inbox."""
        payload = {
            "id": self.post.uuid,
            "title": "Updated Title",
            "content": "Updated Content",
            "visibility": 2
        }
        
        response = self.client.put(self.inbox_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Update post successfully.")
        
        # Refresh the post object from the database and check that it was updated
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, payload["title"])
        self.assertEqual(self.post.content, payload["content"])
        self.assertEqual(self.post.visibility, payload["visibility"])
        
    
    def test_update_nonexsitent_post(self):
        # add post into inbox
        payload = {
            "type": "post",
            "id": f"http://localhost:8000/api/authors/{self.user.uuid}/posts/{self.post.uuid}",
            "description": "This post is a test",
            "contentType": "text/plain",
            "content": "This is a test post",
            "title": "Test Post",
            "published": "2024-10-19T13:07:04+00:00",
            "visibility": 1,
        }

        response = self.client.post(self.inbox_url, data=payload, format='json')
        # try update post
        """Test updating an existing post in the inbox."""
        payload = {
            "id": "2677192c-bce3-4583-afe3-b6592155fe4c",
            "title": "Updated Title",
            "content": "Updated Content",
            "visibility": 2
        }
        
        response = self.client.put(self.inbox_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "No post founded")
        
    
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
            "published": "2024-10-19T13:07:04+00:00",
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
            "published": "2024-10-19T13:07:04+00:00",
            "visibility": 1,
        }

        response = self.client.post(self.inbox_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


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
            "published": "2024-10-19T12:00:00Z",
            "comment": "Nice post!",
            "contentType": "text/plain"
        }

        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        response = self.client.post(self.inbox_url, data=payload, format='json')
        self.assertEqual(len(inbox_obj.items.all()), 1)
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

        inbox_obj = Inbox.objects.get(user=self.user.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(inbox_obj.items.all()), 1)
        self.assertEqual(response.data["message"], "Notice post's owner about your like successfully")
        

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
