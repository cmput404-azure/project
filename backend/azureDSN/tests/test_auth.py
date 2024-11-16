from ..models import User, SiteConfiguration
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch
class RegisterViewTest(APITestCase):
    patch('azureDSN.utils.auth.TokenOrBasicAuthPermission.has_permission', return_value=True).start()
    def setUp(self):
        self.client = APIClient()

        self.username = 'testuser'
        self.password = 'azure404'
        self.email = 'testuser@example.com'
        self.name = 'Test User'
        self.host = 'http://localhost:8000'
        self.github = ''

        # Ensure there's a SiteConfiguration object in the database for testing
        self.site_config, _ = SiteConfiguration.objects.get_or_create(
            defaults={'require_approval': False}  # Set default to False
        )
        # If it already exists, update it
        self.site_config.require_approval = False
        self.site_config.save()

    def test_success_register(self):
        url = reverse('register')
        response = self.client.post(url, {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'name': self.name,
            'host': self.host,
            'githubUsername': self.github
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], "User registered successfully.")

    def test_success_register_requires_approval(self):
        self.site_config.require_approval = True
        self.site_config.save()

        url = reverse('register')
        response = self.client.post(url, {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'name': self.name,
            'host': self.host,
            'githubUsername': self.github
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], "Registration pending approval.")

    def test_fail_register_duplicate_username(self):
        url = reverse('register')
        response = self.client.post(url, {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'name': self.name,
            'host': self.host,
            'githubUsername': self.github
        })

        self.assertEqual(response.status_code, 201)

        response = self.client.post(url, {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'name': self.name,
            'host': self.host,
            'githubUsername': self.github
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], "Username already taken.")

    def test_success_login(self):
        url = reverse('register')
        response = self.client.post(url, {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'name': self.name,
            'host': self.host,
            'githubUsername': self.github
        })

        self.assertEqual(response.status_code, 201)

        url = reverse('login')
        response = self.client.post(url, {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_authenticated']) # checks if the user was successfully logged in

    def test_success_login_with_approval_required(self):
        self.site_config.require_approval = True
        self.site_config.save()

        url = reverse('register')
        response = self.client.post(url, {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'name': self.name,
            'host': self.host,
            'githubUsername': self.github
        })

        self.assertEqual(response.status_code, 201)

        # Demonstrate admin approving the user
        user = User.objects.get(username=self.username)
        user.is_active = True
        user.save()

        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_authenticated'])

    def test_success_login_permission_auto_changed(self):
        self.site_config.require_approval = True
        self.site_config.save()

        url = reverse('register')
        response = self.client.post(url, {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'name': self.name,
            'host': self.host,
            'githubUsername': self.github
        })

        self.assertEqual(response.status_code, 201)

        self.site_config.require_approval = False
        self.site_config.save()

        # by this point, unapproved users should be automatically be approved when logging in
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_authenticated']) # successfully logged in

    def test_fail_login_with_approval_required(self):
        self.site_config.require_approval = True
        self.site_config.save()

        url = reverse('register')
        response = self.client.post(url, {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'name': self.name,
            'host': self.host,
            'githubUsername': self.github
        })

        self.assertEqual(response.status_code, 201)

        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['message'], 'Your account is pending approval.')

    def test_fail_login_incorrect_password(self):
        url = reverse('register')
        response = self.client.post(url, {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'name': self.name,
            'host': self.host,
            'githubUsername': self.github
        })

        self.assertEqual(response.status_code, 201)

        url = reverse('login')
        response = self.client.post(url, {
            'username': self.username,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['message'], 'Login failed. Please check your credentials.')

    def test_logout(self):
        url = reverse('register')
        response = self.client.post(url, {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'name': self.name,
            'host': self.host,
            'githubUsername': self.github
        })

        self.assertEqual(response.status_code, 201)

        url = reverse('login')
        response = self.client.post(url, {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_authenticated']) # checks if the user was successfully logged in

        url = reverse('logout')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['message'], "Logout successful")
    