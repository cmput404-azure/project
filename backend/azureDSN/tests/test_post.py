from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import User, Post
from rest_framework.authtoken.models import Token
from django.utils import timezone

class PostTests(APITestCase):
    
    def setUp(self):
        """Create test users and posts for the tests."""
        self.test_author = User.objects.create_user(
            username='testauthor',
            display_name='Test Author',
            host='http://localhost:8000/api/',
            github='http://github.com',
            page='http://localhost:8000/api/authors/testauthor',
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

    """
    URL: ://service/api/posts/{POST_FQID}
    test:
    
    GET [local] get the public post whose URL is POST_FQID
        friends-only posts: must be authenticated
    """
    # TODO: test getting post by fqid
    # def test_get_post_by_fqid(self):
    
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
    
    # test getting posts paginated
    def test_get_all_public_posts(self):
        """Test retrieving recent posts from an author."""
        url = reverse('create_post', kwargs={'author_serial': self.test_author.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['src']), 0)
        
    def test_get_all_posts_authenticated_as_author(self):
        """Test retrieving all posts when authenticated as the author."""
        self.authenticate()
        
        url = reverse('create_post', kwargs={'author_serial': self.test_author.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # check that we actually got all two posts, the second one is friends-only so it
        # should be included in the response
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
            "visibility": 1
        }
        response = self.client.post(url, post_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check if post actually exists
        self.assertTrue(Post.objects.filter(title=post_data['title']).exists())
        self.assertEqual(response.data['title'], post_data['title'])
        self.assertEqual(response.data['content'], post_data['content'])
        self.assertEqual(response.data['visibility'], post_data['visibility'])

