"""
Pytest configuration for E2E tests with Playwright.

This file provides fixtures and configuration for end-to-end testing:
- Django server setup (live_server)
- Playwright browser configuration
- Test user creation
- Database cleanup
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from playwright.sync_api import Browser, Page, BrowserContext

User = get_user_model()


@pytest.fixture(scope="session")
def django_db_setup():
    """Setup test database for E2E tests"""
    pass


@pytest.fixture(scope="function")
def test_user(db):
    """Create a test user for E2E tests"""
    user = User.objects.create_user(
        username='e2e_testuser',
        email='e2e@test.com',
        password='testpass123'
    )
    return user


@pytest.fixture(scope="function")
def authenticated_page(page: Page, test_user, live_server):
    """
    Provide an authenticated Playwright page.

    This fixture logs in the test user and returns the page ready for testing.
    """
    # Navigate to login page
    page.goto(f"{str(live_server)}/accounts/login/")

    # Fill in login form
    page.fill('input[name="username"]', 'e2e_testuser')
    page.fill('input[name="password"]', 'testpass123')

    # Submit form
    page.click('button[type="submit"]')

    # Wait for redirect to home page
    page.wait_for_url(f"{str(live_server)}/")

    return page
