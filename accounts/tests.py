from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class AuthenticationTestCase(TestCase):
    """Test cases for authentication"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_registration(self):
        """Test user registration"""
        data = {
            'username': 'newuser',
            'password1': 'newpass123!',
            'password2': 'newpass123!'
        }
        response = self.client.post(reverse('register'), data)

        # Should redirect to login page after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        """Test user login"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('login'), data)

        # Should redirect to dashboard after successful login
        self.assertEqual(response.status_code, 302)

    def test_user_logout(self):
        """Test user logout"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('logout'))

        # Should redirect after logout
        self.assertEqual(response.status_code, 302)

    def test_profile_view_requires_login(self):
        """Test that profile view requires authentication"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_profile_view_authenticated(self):
        """Test profile view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_edit_profile(self):
        """Test profile editing"""
        self.client.login(username='testuser', password='testpass123')

        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'updated@example.com'
        }
        response = self.client.post(reverse('edit_profile'), data)

        # Should redirect after successful update
        self.assertEqual(response.status_code, 302)

        # Check if user was updated
        updated_user = User.objects.get(username='testuser')
        self.assertEqual(updated_user.first_name, 'Test')
        self.assertEqual(updated_user.last_name, 'User')
        self.assertEqual(updated_user.email, 'updated@example.com')

    def test_password_change(self):
        """Test password change"""
        self.client.login(username='testuser', password='testpass123')

        data = {
            'old_password': 'testpass123',
            'new_password1': 'newpass456!',
            'new_password2': 'newpass456!'
        }
        response = self.client.post(reverse('change_password'), data)

        # Should redirect after successful password change
        self.assertEqual(response.status_code, 302)

        # Test login with new password
        self.client.logout()
        login_success = self.client.login(username='testuser', password='newpass456!')
        self.assertTrue(login_success)

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('login'), data)

        # Should stay on login page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')

    def test_registration_password_mismatch(self):
        """Test registration with password mismatch"""
        data = {
            'username': 'newuser',
            'password1': 'newpass123!',
            'password2': 'differentpass123!'
        }
        response = self.client.post(reverse('register'), data)

        # Should stay on registration page with error
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_registration_weak_password(self):
        """Test registration with weak password"""
        data = {
            'username': 'newuser',
            'password1': '123',
            'password2': '123'
        }
        response = self.client.post(reverse('register'), data)

        # Should stay on registration page with error
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_duplicate_username_registration(self):
        """Test registration with existing username"""
        data = {
            'username': 'testuser',  # Already exists
            'password1': 'newpass123!',
            'password2': 'newpass123!'
        }
        response = self.client.post(reverse('register'), data)

        # Should stay on registration page with error
        self.assertEqual(response.status_code, 200)
        # Should still have only one user with this username
        self.assertEqual(User.objects.filter(username='testuser').count(), 1)
