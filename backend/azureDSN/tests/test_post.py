from unittest.mock import patch
from uuid import uuid4
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import User, Post, Follow
from rest_framework.authtoken.models import Token
from django.utils import timezone

class PostTests(APITestCase):
    patch('azureDSN.utils.auth.TokenOrBasicAuthPermission.has_permission', return_value=True).start()
    def setUp(self):
        """Create test users and posts for the tests."""
        self.test_author = User.objects.create_user(
            username='testauthor',
            display_name='Test Author',
            host=f"{settings.BASE_URL}/api/",
            github='http://github.com',
            page=f'{settings.BASE_URL}/api/authors/testauthor',
        )
        
        self.test_author2 = User.objects.create_user(
            username='testauthor2',
            display_name='Test Author 2',
            host=f'{settings.BASE_URL}/api/',
            github='http://github.com',
            page=f'{settings.BASE_URL}/api/authors/testauthor2',
        )
        
        # Create a token for the test user
        self.test_token = Token.objects.create(user=self.test_author)

        self.test_post1 = Post.objects.create(
            user=self.test_author,
            title="Test Post 1",
            content="This is the first test post.",
            visibility=1  # Public
        )

        self.test_post2 = Post.objects.create(
            user=self.test_author,
            title="Test Post 2",
            content="This is the second test post.",
            visibility=2  # Friends-only
        )
        
        self.test_post3 = Post.objects.create(
            user=self.test_author,
            title="Test Post 3",
            content="This is the third test post.",
            visibility=3  # Unlisted
        )
        
        self.test_post4 = Post.objects.create(
            user=self.test_author,
            title="Test Post 4",
            content="This is the fourth test post.",
            visibility=4  # Deleted
        )
        
        # post not made by the first test author
        self.test_post5 = Post.objects.create(
            user=self.test_author2,
            title="Test Post 5",
            content="This is the fifth test post.",
            visibility=1  # Public
        )
    
    # authenticate the test user above
    def authenticate(self):
        """Authenticate using the test user's token."""
        self.client.force_authenticate(user=self.test_author)
    
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}
    test:
     
    GET [local, remote] get the public post whose serial is POST_SERIAL
      friends-only posts: must be authenticated
      
    DELETE [local] remove a
      local posts: must be authenticated locally as the author
    
    PUT [local] update a post
      local posts: must be authenticated locally as the author
    """
    
    # ------------------------200 OK------------------------
    # get public post by author and post serial
    def test_get_post(self):
        """Test getting a post by author and post serial."""
        url = reverse('author_post', kwargs={
            'author_serial': self.test_author.uuid,
            'post_serial': self.test_post1.uuid
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.test_post1.title)
        self.assertEqual(response.data['content'], self.test_post1.content)
    
    # get friends-only post
    def test_get_friends_only_post(self):
        """Test getting a friends-only post by author and post serial."""
        self.authenticate()
        url = reverse('author_post', kwargs={
            'author_serial': self.test_author.uuid,
            'post_serial': self.test_post2.uuid
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    # get unlisted post
    def test_get_unlisted_post(self):
        """Test getting an unlisted post by author and post serial."""
        self.authenticate()
        url = reverse('author_post', kwargs={
            'author_serial': self.test_author.uuid,
            'post_serial': self.test_post3.uuid
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    # update post by author and post serial
    def test_update_post(self):
        """Test updating a post by author and post serial."""
        self.authenticate()

        url = reverse('author_post', kwargs={
            'author_serial': self.test_author.uuid,
            'post_serial': self.test_post1.uuid
        })

        updated_data = {
            "title": "Updated Test Post 1",
            "content": "This is the updated content of the first test post.",
            "visibility": 2
        }
        response = self.client.put(url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_post1.refresh_from_db()

        # check that the post was atcually updated
        self.assertEqual(self.test_post1.title, updated_data['title'])
        self.assertEqual(self.test_post1.content, updated_data['content'])
        self.assertEqual(self.test_post1.visibility, updated_data['visibility'])

    # delete post by author and post serial
    def test_delete_post(self):
        """Test deleting a post by author and post serial."""
        self.authenticate()

        url = reverse('author_post', kwargs={
            'author_serial': self.test_author.uuid,
            'post_serial': self.test_post1.uuid
        })
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the post was marked as deleted (visibility changed to 4)
        self.test_post1.refresh_from_db()
        self.assertEqual(self.test_post1.visibility, 4)

        self.assertEqual(response.data['message'], f"Deleted {self.test_post1.uuid}")
        #check that post still aactually exists but is marked as deleted with the visibility
        self.assertTrue(Post.objects.filter(uuid=self.test_post1.uuid).exists())
    
    # ------------------------404 Not Found------------------------
    
    # get post that does not exist
    def test_get_post_not_found(self):
        """Test getting a post that does not exist."""
        url = reverse('author_post', kwargs={
            'author_serial': self.test_author.uuid,
            'post_serial': str(uuid4())
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    # get a deleted post
    def test_get_deleted_post(self):
        """Test getting a deleted post by author and post serial."""
        self.authenticate()
        url = reverse('author_post', kwargs={
            'author_serial': self.test_author.uuid,
            'post_serial': self.test_post4.uuid
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    # update post that does not exist
    def test_update_post_not_found(self):
        """Test updating a post that does not exist."""
        self.authenticate()
        url = reverse('author_post', kwargs={
            'author_serial': self.test_author.uuid,
            'post_serial': str(uuid4())
        })
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # delete post that does not exist
    def test_delete_post_not_found(self):
        """Test deleting a post that does not exist."""
        self.authenticate()
        url = reverse('author_post', kwargs={
            'author_serial': self.test_author.uuid,
            'post_serial': str(uuid4())
        })
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # ------------------------403 Forbidden------------------------
    # get a friends-only post without authentication
    def test_get_friends_only_post_not_authenticated(self):
        """Test getting a friends-only post without authentication."""
        url = reverse('author_post', kwargs={
            'author_serial': self.test_author.uuid,
            'post_serial': self.test_post2.uuid
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    # get an unlisted post without authentication
    def test_get_unlisted_post_not_authenticated(self):
        """Test getting an unlisted post without authentication."""
        url = reverse('author_post', kwargs={
            'author_serial': self.test_author.uuid,
            'post_serial': self.test_post3.uuid
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    # update a post without authentication
    def test_update_post_not_authenticated(self):
        """Test updating a post without authentication."""
        url = reverse('author_post', kwargs={
            'author_serial': self.test_author.uuid,
            'post_serial': self.test_post1.uuid
        })
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    # delete a post without authentication
    def test_delete_post_not_authenticated(self):
        """Test deleting a post without authentication."""
        url = reverse('author_post', kwargs={
            'author_serial': self.test_author.uuid,
            'post_serial': self.test_post1.uuid
        })
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    """
    URL: ://service/api/posts/{POST_FQID}
    test:
    
    GET [local] get the public post whose URL is POST_FQID
        friends-only posts: must be authenticated
    """
    # ------------------------200 OK------------------------
    # get post by fqid
    def test_get_post_by_fqid(self):
        host = f"{settings.BASE_URL}/api/posts/"
        url = reverse('post', kwargs={'post_fqid': f"{host}{self.test_post1.uuid}"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.test_post1.title)
        self.assertEqual(response.data['content'], self.test_post1.content)
        
    # get friends-only post by fqid
    def test_get_friends_only_post_by_fqid(self):
        """Test getting a friends-only post by fqid."""
        self.authenticate()
        host = f"{settings.BASE_URL}/api/posts/"
        url = reverse('post', kwargs={'post_fqid': f"{host}{self.test_post2.uuid}"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # get unlisted post by fqid
    def test_get_unlisted_post_by_fqid(self):
        """Test getting an unlisted post by fqid."""
        self.authenticate()
        host = f"{settings.BASE_URL}/api/posts/"
        url = reverse('post', kwargs={'post_fqid': f"{host}{self.test_post3.uuid}"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # ------------------------404 Not Found------------------------
    # get post by fqid that does not exist
    def test_get_post_by_fqid_not_found(self):
        """Test getting a post by fqid that does not exist."""
        host = f"{settings.BASE_URL}/api/posts/"
        url = reverse('post', kwargs={'post_fqid': f"{host}{uuid4()}"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # get a deleted post by fqid
    def test_get_deleted_post_by_fqid(self):
        """Test getting a deleted post by fqid."""
        host = f"{settings.BASE_URL}/api/posts/"
        url = reverse('post', kwargs={'post_fqid': f"{host}{self.test_post4.uuid}"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # ------------------------403 Forbidden------------------------
    # get a friends-only post by fqid without authentication
    def test_get_friends_only_post_by_fqid_not_authenticated(self):
        """Test getting a friends-only post by fqid without authentication."""
        host = f"{settings.BASE_URL}/api/posts/"
        url = reverse('post', kwargs={'post_fqid': f"{host}{self.test_post2.uuid}"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    # get an unlisted post by fqid without authentication
    def test_get_unlisted_post_by_fqid_not_authenticated(self):
        """Test getting an unlisted post by fqid without authentication."""
        host = f"{settings.BASE_URL}/api/posts/"
        url = reverse('post', kwargs={'post_fqid': f"{host}{self.test_post3.uuid}"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    """
    Creation URL ://service/api/authors/{AUTHOR_SERIAL}/posts/
    test:
    
    GET [local, remote] get the recent posts from author AUTHOR_SERIAL (paginated)
        Not authenticated: only public posts.
        Authenticated locally as author: all posts.
        Authenticated locally as friend of author: public + friends-only posts.
        Authenticated as remote node: This probably should not happen. Remember, the way remote node becomes aware of local posts is by local node pushing those posts to inbox, not by remote node pulling.
        
    POST [local] create a new post but generate a new ID
        Authenticated locally as author
    """
    # ------------------------200 OK------------------------
    # test getting all public posts without authentication
    def test_get_all_posts_not_authenticated(self):
        """Test retrieving all public posts when not authenticated."""
        url = reverse('create_post', kwargs={'author_serial': self.test_author.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # check that we actually got only ONE post, the first test post is public so it should be included in the response
        self.assertEqual(len(response.data['src']), 1)
        self.assertEqual(response.data['src'][0]['title'], self.test_post1.title)
    
    # test getting all posts authenticated as the author
    def test_get_all_posts_authenticated_as_author(self):
        """Test retrieving all posts when authenticated as the author."""
        self.authenticate()
        
        url = reverse('create_post', kwargs={'author_serial': self.test_author.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # check that we actually got all THREE posts, the second and third test posts are friends-only and unlisted so they
        # should be included in the response, the fourth one is deleted so it should not be included
        self.assertEqual(len(response.data['src']), 3)
        post_titles = [post['title'] for post in response.data['src']]
        self.assertIn(self.test_post1.title, post_titles)
        self.assertIn(self.test_post2.title, post_titles)
        self.assertIn(self.test_post3.title, post_titles)

    # test getting all posts authenticated as a friend of the author
    def test_get_all_posts_authenticated_as_friend(self):
        """Test retrieving all posts when authenticated as a friend of the author."""
        self.client.force_authenticate(user=self.test_author2)
        Follow.objects.create(local_follower_id=self.test_author2.uuid, local_followee_id=self.test_author.uuid)
        Follow.objects.create(local_follower_id=self.test_author.uuid, local_followee_id=self.test_author2.uuid)
        
        url = reverse('create_post', kwargs={'author_serial': self.test_author.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # check that we actually got all TWO posts, the third test post is an unlisted post so it
        # should not be included in the response, the fourth one is deleted so it should not be included
        self.assertEqual(len(response.data['src']), 2)
        post_titles = [post['title'] for post in response.data['src']]
        self.assertIn(self.test_post1.title, post_titles)
        self.assertIn(self.test_post2.title, post_titles)

    # test making posts as author
    def test_create_post(self):
        """Test creating a new post when authenticated as the author."""
        self.authenticate()
        
        url = reverse('create_post', kwargs={'author_serial': self.test_author.uuid})
        
        # Data to be sent in the POST request
        post_data = {
            "type": "post",
            "title": "A Test Post Title",
            "description": "This is a test post.",
            "contentType": "text/plain",
            "content": "This is the content of the post.",
            "published": timezone.now().isoformat(),
            "visibility": 1 # We supply number, but it will be converted to string to adhere to response structure
        }
        response = self.client.post(url, post_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check if post actually exists
        self.assertTrue(Post.objects.filter(title=post_data['title']).exists())
        self.assertEqual(response.data['title'], post_data['title'])
        self.assertEqual(response.data['content'], post_data['content'])
        self.assertEqual(response.data['visibility'], "PUBLIC")
        
    # ------------------------404 Not Found------------------------
    # test getting all posts from an author that does not exist
    def test_get_all_posts_author_not_found(self):
        """Test retrieving all posts from an author that does not exist. They will try to find in remote"""
        url = reverse('create_post', kwargs={'author_serial': str(uuid4())})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------401 Unauthorized------------------------
    # test getting public AND friends-only posts without authentication
    def test_get_friends_only_posts_not_authenticated(self):
        """Test retrieving friends-only posts without authentication."""
        url = reverse('create_post', kwargs={'author_serial': self.test_author.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # should only get the first test post since it is public and 
        # since we are not authenticated, we are not allowed to get 
        # the friends only post
        self.assertEqual(len(response.data['src']), 1)
    
    # test creating a post without authentication
    def test_create_post_not_authenticated(self):
        """Test creating a new post without authentication."""
        url = reverse('create_post', kwargs={'author_serial': self.test_author.uuid})
        
        # Data to be sent in the POST request
        post_data = {
            "type": "post",
            "title": "A Test Post Title",
            "description": "This is a test post.",
            "contentType": "text/plain",
            "content": "This is the content of the post.",
            "published": timezone.now().isoformat(),
            "visibility": 1
        }
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)