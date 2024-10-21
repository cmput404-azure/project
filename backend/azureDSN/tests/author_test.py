from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import User

class AuthorTests(APITestCase):

    def setUp(self):
        """Create test users for the tests."""
        self.test_author = User.objects.create_user(
            username='testauthor',
            display_name='Test Author',
            host='http://localhost:8000/api/',
            github='github.com/testauthor',
            page='http://localhost:8000/api/authors/testauthor',
            created_at='2024-10-21T00:00:00Z',
            modified_at='2024-10-21T00:00:00Z'
        )
        self.test_author2 = User.objects.create_user(
            username='testauthor2',
            display_name='Test Author2',
            host='http://localhost:8000/api/',
            github='github.com/testauthor2',
            page='http://localhost:8000/api/authors/testauthor2',
            created_at='2024-10-21T00:00:00Z',
            modified_at='2024-10-21T00:00:00Z'
        )
        self.test_author3 = User.objects.create_user(
            username='testauthor3',
            display_name='Test Author3',
            host='http://localhost:8000/api/',
            github='github.com/testauthor3',
            page='http://localhost:8000/api/authors/testauthor3',
            created_at='2024-10-21T00:00:00Z',
            modified_at='2024-10-21T00:00:00Z'
        )
        self.test_author4 = User.objects.create_user(
            username='testauthor4',
            display_name='Test Author4',
            host='http://localhost:8000/api/',
            github='github.com/testauthor4',
            page='http://localhost:8000/api/authors/testauthor4',
            created_at='2024-10-21T00:00:00Z',
            modified_at='2024-10-21T00:00:00Z'
        )
        self.test_author5 = User.objects.create_user(
            username='testauthor5',
            display_name='Test Author5',
            host='http://localhost:8000/api/',
            github='github.com/testauthor5',
            page='http://localhost:8000/api/authors/testauthor5',
            created_at='2024-10-21T00:00:00Z',
            modified_at='2024-10-21T00:00:00Z'
        )
        self.test_author6 = User.objects.create_user(
            username='testauthor6',
            display_name='Test Author6',
            host='http://localhost:8000/api/',
            github='github.com/testauthor6',
            page='http://localhost:8000/api/authors/testauthor6',
            created_at='2024-10-21T00:00:00Z',
            modified_at='2024-10-21T00:00:00Z'
        )
        self.test_author7 = User.objects.create_user(
            username='testauthor7',
            display_name='Test Author7',
            host='http://localhost:8000/api/',
            github='github.com/testauthor7',
            page='http://localhost:8000/api/authors/testauthor7',
            created_at='2024-10-21T00:00:00Z',
            modified_at='2024-10-21T00:00:00Z'
        )

    # test getting all authors
    def test_retrieve_authors_all(self):
        """Test retrieving all authors without pagination."""
        url = reverse('authors_all')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        payload = response.data
        self.assertEqual(len(payload), 7)
        for author in payload:
            print(author)
            self.assertEqual(author["type"], "author")
            self.assertIn(author["id"], [str(self.test_author.uuid), str(self.test_author2.uuid), str(self.test_author3.uuid), str(self.test_author4.uuid), str(self.test_author5.uuid), str(self.test_author6.uuid), str(self.test_author7.uuid)])
            self.assertIn(author["displayName"], ['Test Author', 'Test Author2', 'Test Author3', 'Test Author4', 'Test Author5', 'Test Author6', 'Test Author7'])
            self.assertIn(author["host"], ['http://localhost:8000/api/'])
            self.assertIn(author["github"], ['github.com/testauthor', 'github.com/testauthor2', 'github.com/testauthor3', 'github.com/testauthor4', 'github.com/testauthor5', 'github.com/testauthor6', 'github.com/testauthor7'])
            self.assertIn(author["page"], ['http://localhost:8000/api/authors/testauthor', 'http://localhost:8000/api/authors/testauthor2', 'http://localhost:8000/api/authors/testauthor3', 'http://localhost:8000/api/authors/testauthor4', 'http://localhost:8000/api/authors/testauthor5', 'http://localhost:8000/api/authors/testauthor6', 'http://localhost:8000/api/authors/testauthor7'])
        
    # def test_retrieve_authors_paginated(self):
    #     """Test retrieving all authors with pagination."""
    #     url = reverse('authors_all')
        
    #     # Simulate paginated response (e.g., page 1, size 3)
    #     response = self.client.get(url, {'page': 1, 'page_size': 3})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    #     payload = response.data
    #     self.assertEqual(payload["type"], "authors")
    #     self.assertEqual(len(payload["authors"]), 3)  # Check if 3 authors were returned on the first page

    #     # Check pagination metadata if it's returned
    #     pagination = PageNumberPagination()
    #     pagination.page_size = 3
    #     authors = User.objects.all()
    #     paginated_authors = pagination.paginate_queryset(authors, request=None)
    #     self.assertEqual(len(paginated_authors), 3)  # Ensure only 3 authors are paginated on page 1

    #     # Check if next and previous pagination links exist (if applicable)
    #     self.assertIn('next', response.data)
    #     self.assertIn('previous', response.data)
    
    # test getting author by uuid
    def test_get_author_by_uuid(self):
        """Test retrieving an author by UUID."""
        url = reverse('author_serial', kwargs={'author_serial': self.test_author.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['displayName'], self.test_author.display_name)

    # test getting author by fqid
    def test_get_author_by_fqid(self):
        """Test retrieving an author by FQID."""
        host = "http://localhost:8000/api/authors/"
        url = reverse('author_fqid', kwargs={'author_fqid': f"{host}{self.test_author.uuid}"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(response.data['type'], 'author')
        self.assertEqual(response.data['id'], f"{self.test_author.uuid}")
        self.assertEqual(response.data['displayName'], self.test_author.display_name)
        self.assertEqual(response.data['host'], 'http://localhost:8000/api/')
        self.assertEqual(response.data['github'], 'github.com/testauthor')
        self.assertEqual(response.data['page'], 'http://localhost:8000/api/authors/testauthor')



