"""
Custom django-allauth adapters for security.
"""

from allauth.account.adapter import DefaultAccountAdapter
from django.core.exceptions import PermissionDenied


class NoSignupAccountAdapter(DefaultAccountAdapter):
    """
    Disable public signup completely.
    Users can only be created via Django admin by superusers.

    This prevents:
    - Bot registrations
    - Spam accounts
    - Unauthorized access
    - Database pollution
    """

    def is_open_for_signup(self, request):
        """
        Disable public signup.
        Return False to block /accounts/signup/ endpoint.
        """
        return False

    def save_user(self, request, user, form, commit=True):
        """
        Block user creation via signup form.
        Raise PermissionDenied to ensure no signup happens.
        """
        raise PermissionDenied("Public signup is disabled. Contact admin for access.")
