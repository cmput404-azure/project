from uuid import uuid4
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import User
from unittest.mock import patch

class AuthorTests(APITestCase):
    patch('azureDSN.utils.auth.TokenOrBasicAuthPermission.has_permission', return_value=True).start()
    def setUp(self):
        """Create test users for the tests."""
        self.test_author = User.objects.create_user(
            type='author',
            username='testauthor',
            display_name='Test Author',
            host=f"{settings.BASE_URL}/api/",
            github='https://github.com/testauthor',
            page=f'{settings.BASE_URL}/authors/testauthor',
            created_at='2024-10-21T00:00:00Z',
            modified_at='2024-10-21T00:00:00Z'
        )
        self.test_author2 = User.objects.create_user(
            type='author',
            username='testauthor2',
            display_name='Test Author2',
            host=f"{settings.BASE_URL}/api/",
            github='https://github.com/testauthor2',
            page=f'{settings.BASE_URL}/authors/testauthor2',
            created_at='2024-10-21T00:00:00Z',
            modified_at='2024-10-21T00:00:00Z'
        )
        self.test_author3 = User.objects.create_user(
            type='author',
            username='testauthor3',
            display_name='Test Author3',
            host=f"{settings.BASE_URL}/api/",
            github='https://github.com/testauthor3',
            page=f'{settings.BASE_URL}/authors/testauthor3',
            created_at='2024-10-21T00:00:00Z',
            modified_at='2024-10-21T00:00:00Z'
        )
        self.test_author4 = User.objects.create_user(
            type='author',
            username='testauthor4',
            display_name='Test Author4',
            host=f"{settings.BASE_URL}/api/",
            github='https://github.com/testauthor4',
            page=f'{settings.BASE_URL}/authors/testauthor4',
            created_at='2024-10-21T00:00:00Z',
            modified_at='2024-10-21T00:00:00Z'
        )
        self.test_author5 = User.objects.create_user(
            type='author',
            username='testauthor5',
            display_name='Test Author5',
            host=f"{settings.BASE_URL}/api/",
            github='https://github.com/testauthor5',
            page=f'{settings.BASE_URL}/authors/testauthor5',
            created_at='2024-10-21T00:00:00Z',
            modified_at='2024-10-21T00:00:00Z'
        )
        self.test_author6 = User.objects.create_user(
            type='author',
            username='testauthor6',
            display_name='Test Author6',
            host=f"{settings.BASE_URL}/api/",
            github='https://github.com/testauthor6',
            page=f'{settings.BASE_URL}/authors/testauthor6',
            created_at='2024-10-21T00:00:00Z',
            modified_at='2024-10-21T00:00:00Z'
        )
        self.test_author7 = User.objects.create_user(
            type='author',
            username='testauthor7',
            display_name='Test Author7',
            host=f"{settings.BASE_URL}/api/",
            github='https://github.com/testauthor7',
            page=f'{settings.BASE_URL}/authors/testauthor7',
            created_at='2024-10-21T00:00:00Z',
            modified_at='2024-10-21T00:00:00Z'
        )

    # ----------------------------200 Tests----------------------------

    # test getting all authors
    def test_retrieve_authors_all(self):
        """Test retrieving all authors without pagination."""
        url = reverse('authors_all')
        string_uuid = str(self.test_author.uuid)
        url_with_params = f"{url}?user={string_uuid}"
        response = self.client.get(url_with_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        payload = response.data
        self.assertEqual(len(payload), 6)
        for author in payload:
            self.assertIn(author["displayName"], ['Test Author2', 'Test Author3', 'Test Author4', 'Test Author5', 'Test Author6', 'Test Author7'])
            self.assertIn(author["host"], [f"{settings.BASE_URL}/api/"])
            self.assertIn(author["github"], ['https://github.com/testauthor2', 'https://github.com/testauthor3', 'https://github.com/testauthor4', 'https://github.com/testauthor5', 'https://github.com/testauthor6', 'https://github.com/testauthor7'])
            self.assertIn(author["page"], [f'{settings.BASE_URL}/authors/testauthor', f'{settings.BASE_URL}/authors/testauthor2', f'{settings.BASE_URL}/authors/testauthor3', f'{settings.BASE_URL}/authors/testauthor4', f'{settings.BASE_URL}/authors/testauthor5', f'{settings.BASE_URL}/authors/testauthor6', f'{settings.BASE_URL}/authors/testauthor7'])

    def test_retrieve_authors_all_anonymous(self):
        """Test retrieving all authors without pagination."""
        url = reverse('authors_all')
        string_uuid = 'anonymous'
        url_with_params = f"{url}?user={string_uuid}"
        response = self.client.get(url_with_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        payload = response.data
        self.assertEqual(len(payload), 7)
          
    # test getting all authors paginated  
    def test_retrieve_authors_paginated(self):
        """Test retrieving authors with pagination."""
        
        url = reverse('authors_list')
        
        # Request the first page with 5 authors per page
        response = self.client.get(url, {'page': 1, 'size': 5})
        
        # Check if the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check pagination metadata and authors data
        payload = response.data
        self.assertIn("type", payload)
        self.assertEqual(payload["type"], "authors")
        
        # Check if we have exactly 5 authors on the first page
        authors_data = payload["authors"]  
        self.assertEqual(len(authors_data), 5)
        
        # check that the first page contains the first 5 authors
        for author in authors_data:
            self.assertIn("displayName", author)
            self.assertIn(author["displayName"], ["Test Author", "Test Author2", "Test Author3", "Test Author4", "Test Author5"])

        # ------SECOND PAGE------

        # Request the second page and check if it contains remaining authors
        response = self.client.get(url, {'page': 2, 'size': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check pagination metadata for the second page
        payload = response.data
        self.assertEqual(payload["type"], "authors")
        
        # Check that the second page contains only 2 authors (remaining ones)
        authors_data = payload["authors"]
        self.assertEqual(len(authors_data), 2)
        
        for author in authors_data:
            self.assertIn("displayName", author)
            self.assertIn(author["displayName"], ["Test Author6", "Test Author7"])
        
    
    # test getting author by uuid
    def test_get_author_by_uuid(self):
        """Test retrieving an author by UUID."""
        url = reverse('author_serial', kwargs={'author_serial': self.test_author.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['displayName'], self.test_author.display_name)
    

    # test updating author by uuid
    def test_update_author_by_uuid(self):
        """Test updating an author by UUID."""
        url = reverse('author_serial', kwargs={'author_serial': self.test_author.uuid})
        updated_data = {
            'id': f"{self.test_author.uuid}",
            'displayName': 'Updated Test Author',
            'host': f"{settings.BASE_URL}/api/",
            'github': 'http://github.com/updated_testauthor',
            'page': f'{settings.BASE_URL}/authors/updated_testauthor',
        }
        response = self.client.put(url, updated_data, format='json')

        self.assertEqual(response.status_code, 200)

        # chcek that the author's details were updated
        self.test_author.refresh_from_db()
        self.assertEqual(str(self.test_author.uuid), updated_data['id']) # make sure its the same user object
        self.assertEqual(self.test_author.display_name, updated_data['displayName'])
        self.assertEqual(self.test_author.host, updated_data['host'])
        self.assertEqual(self.test_author.github, updated_data['github'])
        self.assertEqual(self.test_author.page, updated_data['page'])

    # test getting author by fqid
    def test_get_author_by_fqid(self):
        """Test retrieving an author by FQID."""
        host = f"{settings.BASE_URL}/api/authors/"
        url = reverse('author_fqid', kwargs={'author_fqid': f"{host}{self.test_author.uuid}"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
        self.assertEqual(response.data['type'], 'author')
        self.assertEqual(response.data['id'], f"{settings.BASE_URL}/api/authors/{self.test_author.uuid}")
        self.assertEqual(response.data['displayName'], self.test_author.display_name)
        self.assertEqual(response.data['host'], f'{settings.BASE_URL}/api/')
        self.assertEqual(response.data['github'], 'https://github.com/testauthor')
        self.assertEqual(response.data['page'], f'{settings.BASE_URL}/authors/testauthor')
        
    # # ----------------------------404 Tests----------------------------
    
    def test_get_nonexistent_author_by_uuid(self):
        """Test that retrieving a non-existent author by UUID returns a 404."""
        url = reverse('author_serial', kwargs={'author_serial': uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_nonexistent_author_by_fqid(self):
        """Test that retrieving a non-existent author by FQID returns a 404."""
        host = f"{settings.BASE_URL}/api/authors/"
        url = reverse('author_fqid', kwargs={'author_fqid': f'{host}{uuid4()}'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_nonexistent_author_by_uuid(self):
        """Test that updating a non-existent author by UUID returns a 404."""
        url = reverse('author_serial', kwargs={'author_serial': uuid4()})
        data = {
            'display_name': 'Updated Author'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_update_nonexistent_author_by_fqid(self):
        """Test that updating a non-existent author by FQID returns a 404."""
        host = f"{settings.BASE_URL}/api/authors/"
        url = reverse('author_fqid', kwargs={'author_fqid': f'{host}{uuid4()}'})
        data = {
            'display_name': 'Updated Author'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)