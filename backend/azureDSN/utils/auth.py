import os
from rest_framework.authentication import get_authorization_header
from rest_framework.permissions import BasePermission
from base64 import b64decode
from ..models import NodeUser

# Can be reused in other files
def is_valid_basic_auth(auth_value):
    """
        Validate Basic Auth credentials (for remote requests)
    """
    try:
        # Decode Basic Auth credentials
        decoded_credentials = b64decode(auth_value).decode('utf-8')
        username, password = decoded_credentials.split(':')
        
        # Validate credentials with data stored in database
        node = NodeUser.objects.get(username=username)
        if node.password == password and node.is_authenticated:
            return True
        return False
    except Exception as e:
        return False

class TokenOrBasicAuthPermission(BasePermission):
    def has_permission(self, request, view):
        # Token has higher precedence over BasicAuth
        csrf_token = request.headers.get("X-CSRFToken") if request.headers.get("X-CSRFToken") else request.COOKIES.get('csrftoken')
        if csrf_token:
            return True

        # Check Basic Authentication for remote requests
        auth_header = get_authorization_header(request).split()
        if len(auth_header) == 2 and auth_header[0].lower() == b"basic":
            return is_valid_basic_auth(auth_header[1].decode())
        
        # For backend API calls
        internal_secret = request.headers.get("Internal-Auth")
        if self._is_internal_request(internal_secret):
            return True
        
        # If no CSRF or BasicAuth, check if the request is for the login or register endpoint
        if (request.path).rstrip('/') == '/api/login':
            return True
        
        if (request.path).rstrip('/') == '/api/register':
            return True

        return False
    
    def _is_internal_request(self, secret):
        return secret == os.getenv("INTERNAL_API_SECRET")
