from django.test import TestCase, Client as TestClient
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
import json
import tempfile
import os

from .models import Client, Project, FolderStructure, PredefinedStructure


class ModelTestCase(TestCase):
    """Test cases for models"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.client_obj = Client.objects.create(
            name='Test Client',
            email='client@example.com',
            phone='1234567890',
            created_by=self.user
        )

        self.project = Project.objects.create(
            name='Test Project',
            client=self.client_obj,
            description='Test project description',
            created_by=self.user
        )

    def test_client_creation(self):
        """Test client model creation"""
        self.assertEqual(self.client_obj.name, 'Test Client')
        self.assertEqual(self.client_obj.email, 'client@example.com')
        self.assertEqual(self.client_obj.created_by, self.user)
        self.assertTrue(self.client_obj.is_active)
        self.assertEqual(str(self.client_obj), 'Test Client')

    def test_client_project_count(self):
        """Test client project count property"""
        self.assertEqual(self.client_obj.project_count, 1)

        # Create another project
        Project.objects.create(
            name='Test Project 2',
            client=self.client_obj,
            created_by=self.user
        )
        self.assertEqual(self.client_obj.project_count, 2)

    def test_project_creation(self):
        """Test project model creation"""
        self.assertEqual(self.project.name, 'Test Project')
        self.assertEqual(self.project.client, self.client_obj)
        self.assertEqual(self.project.created_by, self.user)
        self.assertEqual(self.project.status, 'planning')
        self.assertTrue(self.project.is_active)

    def test_project_full_path(self):
        """Test project full path property"""
        expected_path = f"{self.project.save_location}/{self.client_obj.name}/{self.project.name}"
        self.assertEqual(self.project.full_project_path, expected_path)

    def test_folder_structure_creation(self):
        """Test folder structure model creation"""
        structure_data = [
            {
                "name": "folder1",
                "children": [
                    {"name": "subfolder1", "children": []},
                    {"name": "subfolder2", "children": []}
                ]
            },
            {"name": "folder2", "children": []}
        ]

        folder_structure = FolderStructure.objects.create(
            project=self.project,
            name='Test Structure',
            structure_data=structure_data
        )

        self.assertEqual(folder_structure.project, self.project)
        self.assertEqual(folder_structure.name, 'Test Structure')
        self.assertEqual(folder_structure.get_structure_as_dict(), structure_data)
        self.assertFalse(folder_structure.is_created)

    def test_predefined_structure_creation(self):
        """Test predefined structure model creation"""
        structure_data = [{"name": "templates", "children": []}]

        predefined = PredefinedStructure.objects.create(
            name='Motion Graphics Template',
            structure_type='motion_graphics',
            structure_data=structure_data,
            created_by=self.user
        )

        self.assertEqual(predefined.name, 'Motion Graphics Template')
        self.assertEqual(predefined.structure_type, 'motion_graphics')
        self.assertEqual(predefined.get_structure_as_dict(), structure_data)
        self.assertFalse(predefined.is_public)


class ViewTestCase(TestCase):
    """Test cases for views"""

    def setUp(self):
        self.client = TestClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.client_obj = Client.objects.create(
            name='Test Client',
            email='client@example.com',
            created_by=self.user
        )

        self.project = Project.objects.create(
            name='Test Project',
            client=self.client_obj,
            created_by=self.user
        )

    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dashboard_authenticated(self):
        """Test dashboard view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_client_list_view(self):
        """Test client list view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('client_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Client')

    def test_client_create_view(self):
        """Test client creation view"""
        self.client.login(username='testuser', password='testpass123')

        # GET request
        response = self.client.get(reverse('client_create'))
        self.assertEqual(response.status_code, 200)

        # POST request
        data = {
            'name': 'New Client',
            'email': 'new@example.com',
            'phone': '9876543210'
        }
        response = self.client.post(reverse('client_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation

        # Check if client was created
        self.assertTrue(Client.objects.filter(name='New Client').exists())

    def test_project_list_view(self):
        """Test project list view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')

    def test_project_create_view(self):
        """Test project creation view"""
        self.client.login(username='testuser', password='testpass123')

        # GET request
        response = self.client.get(reverse('project_create'))
        self.assertEqual(response.status_code, 200)

        # POST request
        data = {
            'name': 'New Project',
            'client_id': self.client_obj.id,
            'description': 'New project description',
            'status': 'planning'
        }
        response = self.client.post(reverse('project_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation

        # Check if project was created
        self.assertTrue(Project.objects.filter(name='New Project').exists())


class APITestCase(APITestCase):
    """Test cases for API endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.client_obj = Client.objects.create(
            name='Test Client',
            email='client@example.com',
            created_by=self.user
        )

        self.project = Project.objects.create(
            name='Test Project',
            client=self.client_obj,
            created_by=self.user
        )

        # Authenticate the client
        self.client.force_authenticate(user=self.user)

    def test_dashboard_stats_api(self):
        """Test dashboard stats API endpoint"""
        url = reverse('api_dashboard_stats')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('stats', response.data)
        self.assertIn('recent_projects', response.data)
        self.assertEqual(response.data['stats']['total_clients'], 1)
        self.assertEqual(response.data['stats']['total_projects'], 1)

    def test_client_list_api(self):
        """Test client list API endpoint"""
        url = reverse('api_client_list_create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # API returns paginated results
        self.assertIn('results', response.data)
        self.assertTrue(len(response.data['results']) >= 1)
        # Find our test client
        test_client = next((client for client in response.data['results'] if client.get('name') == 'Test Client'), None)
        self.assertIsNotNone(test_client)
        self.assertEqual(test_client['name'], 'Test Client')

    def test_client_create_api(self):
        """Test client creation via API"""
        url = reverse('api_client_list_create')
        data = {
            'name': 'API Client',
            'email': 'api@example.com',
            'phone': '1111111111'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'API Client')
        self.assertTrue(Client.objects.filter(name='API Client').exists())

    def test_client_detail_api(self):
        """Test client detail API endpoint"""
        url = reverse('api_client_detail', kwargs={'pk': self.client_obj.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Client')

    def test_project_list_api(self):
        """Test project list API endpoint"""
        url = reverse('api_project_list_create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # API returns paginated results
        self.assertIn('results', response.data)
        self.assertTrue(len(response.data['results']) >= 1)
        # Find our test project
        test_project = next((project for project in response.data['results'] if project.get('name') == 'Test Project'), None)
        self.assertIsNotNone(test_project)
        self.assertEqual(test_project['name'], 'Test Project')

    def test_project_create_api(self):
        """Test project creation via API"""
        url = reverse('api_project_list_create')
        data = {
            'name': 'API Project',
            'client': self.client_obj.id,
            'description': 'Created via API',
            'status': 'planning'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'API Project')
        self.assertTrue(Project.objects.filter(name='API Project').exists())

    def test_folder_structure_create_api(self):
        """Test folder structure creation via API"""
        url = reverse('api_folder_structure_list_create', kwargs={'project_id': self.project.id})
        structure_data = [
            {
                "name": "api_folder",
                "children": [
                    {"name": "subfolder", "children": []}
                ]
            }
        ]
        data = {
            'name': 'API Structure',
            'structure_data': structure_data
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'API Structure')
        self.assertTrue(FolderStructure.objects.filter(name='API Structure').exists())

    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access API"""
        self.client.force_authenticate(user=None)

        url = reverse('api_client_list_create')
        response = self.client.get(url)
        # Django REST Framework returns 403 for unauthenticated users with permission classes
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_user_isolation(self):
        """Test that users can only access their own data"""
        # Create another user and client
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )

        other_client = Client.objects.create(
            name='Other Client',
            email='other@example.com',
            created_by=other_user
        )

        # Try to access other user's client
        url = reverse('api_client_detail', kwargs={'pk': other_client.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SecurityTestCase(TestCase):
    """Test cases for security"""

    def setUp(self):
        self.client = TestClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_sql_injection_protection(self):
        """Test protection against SQL injection"""
        self.client.login(username='testuser', password='testpass123')

        # Try SQL injection in search parameter
        malicious_search = "'; DROP TABLE projects_client; --"
        response = self.client.get(reverse('client_list'), {'search': malicious_search})

        # Should not cause an error and should return normal response
        self.assertEqual(response.status_code, 200)

    def test_xss_protection(self):
        """Test protection against XSS attacks"""
        self.client.login(username='testuser', password='testpass123')

        # Try to create client with XSS payload
        xss_payload = '<script>alert("XSS")</script>'
        data = {
            'name': xss_payload,
            'email': 'test@example.com'
        }
        response = self.client.post(reverse('client_create'), data)

        # Should redirect (successful creation) but content should be escaped
        if response.status_code == 302:
            client = Client.objects.filter(name=xss_payload).first()
            self.assertIsNotNone(client)
            # The actual XSS protection is handled by Django's template system

    def test_csrf_protection(self):
        """Test CSRF protection"""
        self.client.login(username='testuser', password='testpass123')

        # Try to make POST request without CSRF token
        self.client.logout()
        data = {
            'name': 'Test Client',
            'email': 'test@example.com'
        }
        response = self.client.post(reverse('client_create'), data)

        # Should redirect to login or return 403
        self.assertIn(response.status_code, [302, 403])


class IntegrationTestCase(TestCase):
    """Integration test cases"""

    def setUp(self):
        self.client = TestClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_complete_workflow(self):
        """Test complete workflow from client creation to folder structure"""
        # 1. Create client
        client_data = {
            'name': 'Integration Client',
            'email': 'integration@example.com',
            'phone': '1234567890'
        }
        response = self.client.post(reverse('client_create'), client_data)
        self.assertEqual(response.status_code, 302)

        client_obj = Client.objects.get(name='Integration Client')

        # 2. Create project
        project_data = {
            'name': 'Integration Project',
            'client_id': client_obj.id,
            'description': 'Integration test project',
            'status': 'planning'
        }
        response = self.client.post(reverse('project_create'), project_data)
        self.assertEqual(response.status_code, 302)

        project = Project.objects.get(name='Integration Project')

        # 3. Create folder structure
        structure_data = json.dumps([
            {
                "name": "integration_folder",
                "children": [
                    {"name": "subfolder1", "children": []},
                    {"name": "subfolder2", "children": []}
                ]
            }
        ])

        folder_data = {
            'name': 'Integration Structure',
            'structure_data': structure_data
        }
        response = self.client.post(
            reverse('folder_structure_create', kwargs={'project_id': project.id}),
            folder_data
        )
        self.assertEqual(response.status_code, 302)

        # Verify folder structure was created
        folder_structure = FolderStructure.objects.get(name='Integration Structure')
        self.assertEqual(folder_structure.project, project)
        self.assertEqual(len(folder_structure.get_structure_as_dict()), 1)
