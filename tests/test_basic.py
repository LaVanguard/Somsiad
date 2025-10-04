"""
Basic sanity tests for Law Advisor
Sprint 1 - Foundation tests
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


def test_django_setup():
    """Sanity check: Django is properly configured"""
    assert True, "Django setup working"


@pytest.mark.django_db
def test_user_model_exists():
    """Test that User model is available"""
    assert User is not None
    assert hasattr(User, 'objects')


@pytest.mark.django_db
def test_user_creation():
    """Test creating a basic user"""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.check_password('testpass123')
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser


@pytest.mark.django_db
def test_superuser_creation():
    """Test creating an admin/superuser"""
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    
    assert admin.username == 'admin'
    assert admin.is_superuser
    assert admin.is_staff
    assert admin.is_active


@pytest.mark.django_db
def test_admin_url_exists():
    """Test that admin URL is accessible"""
    client = Client()
    response = client.get('/admin/')
    
    # Should redirect to login (302) or show login page (200)
    assert response.status_code in [200, 302]


@pytest.mark.django_db
def test_admin_login_works():
    """Test admin can login"""
    # Create admin user
    admin = User.objects.create_superuser(
        username='testadmin',
        password='testpass123'
    )
    
    # Login
    client = Client()
    logged_in = client.login(username='testadmin', password='testpass123')
    
    assert logged_in, "Admin should be able to login"
    
    # Access admin panel
    response = client.get('/admin/')
    assert response.status_code == 200