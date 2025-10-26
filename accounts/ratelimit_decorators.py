"""
Rate limiting decorators for security.
Protects endpoints from brute force, spam, and abuse.
"""
from django_ratelimit.decorators import ratelimit
from django.http import HttpResponse
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def ratelimit_login(view_func):
    """
    Protect login endpoint from brute force attacks.
    Limit: 5 attempts per 5 minutes per IP address.
    """
    @wraps(view_func)
    @ratelimit(key='ip', rate='5/5m', method='POST', block=True)
    def wrapper(request, *args, **kwargs):
        # Check if rate limited
        if getattr(request, 'limited', False):
            logger.warning(f"Rate limit exceeded for login from IP: {request.META.get('REMOTE_ADDR')}")
            return HttpResponse(
                '<html><body><h1>Too Many Login Attempts</h1>'
                '<p>You have exceeded the maximum number of login attempts.</p>'
                '<p>Please try again in 5 minutes.</p></body></html>',
                status=429
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def ratelimit_signup(view_func):
    """
    Protect signup endpoint from spam registrations.
    Limit: 3 signups per hour per IP address.
    """
    @wraps(view_func)
    @ratelimit(key='ip', rate='3/1h', method='POST', block=True)
    def wrapper(request, *args, **kwargs):
        if getattr(request, 'limited', False):
            logger.warning(f"Rate limit exceeded for signup from IP: {request.META.get('REMOTE_ADDR')}")
            return HttpResponse(
                '<html><body><h1>Too Many Signup Attempts</h1>'
                '<p>You have exceeded the maximum number of signup attempts.</p>'
                '<p>Please try again in 1 hour.</p></body></html>',
                status=429
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def ratelimit_rag_query(view_func):
    """
    Protect RAG API from abuse (costs money via OpenAI API).
    Limit: 20 queries per minute per user or IP.
    """
    @wraps(view_func)
    @ratelimit(key='user_or_ip', rate='20/1m', method='POST', block=True)
    def wrapper(request, *args, **kwargs):
        if getattr(request, 'limited', False):
            user_id = request.user.id if request.user.is_authenticated else 'anonymous'
            logger.warning(f"Rate limit exceeded for RAG query. User: {user_id}, IP: {request.META.get('REMOTE_ADDR')}")
            return HttpResponse(
                'Rate limit exceeded. Maximum 20 queries per minute.',
                status=429,
                content_type='text/plain'
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def ratelimit_document_upload(view_func):
    """
    Protect document upload from DoS attacks (processing is expensive).
    Limit: 5 uploads per 10 minutes per authenticated user.
    """
    @wraps(view_func)
    @ratelimit(key='user', rate='5/10m', method='POST', block=True)
    def wrapper(request, *args, **kwargs):
        if getattr(request, 'limited', False):
            logger.warning(f"Rate limit exceeded for document upload. User: {request.user.id}")
            return HttpResponse(
                '<div class="text-red-400 text-sm">[ERROR] Too many uploads. Maximum 5 documents per 10 minutes.</div>',
                status=429
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def ratelimit_document_process(view_func):
    """
    Protect document processing from spam (very CPU/API intensive).
    Limit: 10 processing requests per 10 minutes per user.
    """
    @wraps(view_func)
    @ratelimit(key='user', rate='10/10m', method='POST', block=True)
    def wrapper(request, *args, **kwargs):
        if getattr(request, 'limited', False):
            logger.warning(f"Rate limit exceeded for document processing. User: {request.user.id}")
            return HttpResponse(
                '<div class="text-red-400 text-sm">[ERROR] Too many processing requests. Maximum 10 per 10 minutes.</div>',
                status=429
            )
        return view_func(request, *args, **kwargs)
    return wrapper
