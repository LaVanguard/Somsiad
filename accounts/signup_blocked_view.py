"""
Blocked signup view - prevents any signup attempts.
"""
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def signup_blocked(request):
    """
    Block all signup attempts with clear message.
    This replaces django-allauth signup view completely.
    """
    return HttpResponse(
        '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Signup Disabled - Somsiad</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: #1f2937;
                    color: #f3f4f6;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    text-align: center;
                    max-width: 500px;
                    padding: 40px;
                    background: #374151;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                }
                h1 {
                    color: #ef4444;
                    margin-bottom: 20px;
                }
                p {
                    line-height: 1.6;
                    margin-bottom: 30px;
                }
                a {
                    display: inline-block;
                    padding: 12px 24px;
                    background: #3b82f6;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 500;
                }
                a:hover {
                    background: #2563eb;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔒 Public Signup Disabled</h1>
                <p>
                    Public registration is currently disabled for security reasons.
                    This is a private application.
                </p>
                <p>
                    If you need access, please contact the administrator.
                </p>
                <a href="/accounts/login/">Go to Login</a>
            </div>
        </body>
        </html>
        ''',
        status=403
    )
