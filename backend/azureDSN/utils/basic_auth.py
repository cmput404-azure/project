from urllib.parse import urlparse
from rest_framework.permissions import BasePermission
from base64 import b64decode
from ..models import NodeUser
import os

class IsAuthenticatedNode(BasePermission):
    def has_permission(self, request, view):
        # Allow local requests without authentication
        base_url = os.getenv('BASE_URL', '')
        origin_header = request.headers.get('Origin', '')

        print(f"{base_url}, {origin_header}")

        def ensure_scheme(url):
            if not url.startswith(('http://', 'https://')):
                return f'http://{url}'
            return url

        parsed_base_url = urlparse(ensure_scheme(base_url))
        parsed_origin = urlparse(ensure_scheme(origin_header))

        print(f"{parsed_base_url}, {parsed_origin}")

        # Only allow unauthenticated requests that exactly match BASE_URL
        if origin_header and parsed_origin.netloc == parsed_base_url.netloc:
            return True

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Basic '):
            return False

        # Decode Basic Auth credentials
        try:
            encoded_credentials = auth_header.split(' ')[1]
            decoded_credentials = b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':')
            print(username, password)
        except (IndexError, ValueError):
            return False

        origin = f"{parsed_origin.scheme}://{parsed_origin.netloc}"
        # Validate credentials in the database
        try:
            node = NodeUser.objects.get(host=origin)
            return node.username == username and node.password == password and node.is_authenticated
        except NodeUser.DoesNotExist:
            return False
