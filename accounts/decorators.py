"""
Custom decorators for authentication handling.
"""
from functools import wraps
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings


def ajax_login_required(view_func):
    """
    Decorator for views that checks if user is authenticated.

    For AJAX/HTMX requests: Returns an HTML message prompting re-login.
    For regular requests: Redirects to login page.

    This prevents the login form from being loaded into HTMX target elements
    when the user's session expires.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Check if this is an AJAX/HTMX request
            is_ajax = (
                request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                request.headers.get('HX-Request') == 'true'
            )

            if is_ajax:
                # Return a message for AJAX requests instead of login form
                return HttpResponse(
                    '''<div class="text-center py-8 text-gray-400 text-sm">
                        <p class="mb-2">Sesja wygasła</p>
                        <a href="/accounts/login/" class="text-blue-400 hover:text-blue-300">
                            Zaloguj się ponownie
                        </a>
                    </div>''',
                    status=401
                )
            else:
                # Redirect to login for regular requests
                login_url = settings.LOGIN_URL or '/accounts/login/'
                return redirect(f'{login_url}?next={request.path}')

        return view_func(request, *args, **kwargs)

    return wrapper
