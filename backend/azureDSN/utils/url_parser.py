from urllib.parse import urljoin, quote, unquote, urlparse

def get_base_host(url):
    return urljoin(url, '/').rstrip('/')

def extract_uuid(url):
    return url.rstrip('/').split('/')[-1]

def percent_encode(url):
    return quote(url, safe='')

def percent_decode(url):
    return unquote(url)

def is_valid_url(value):
    """
    Validates if a string is a properly formatted URL.
    """
    if not value:
        return False
    parsed_url = urlparse(value)
    return all([parsed_url.scheme, parsed_url.netloc])