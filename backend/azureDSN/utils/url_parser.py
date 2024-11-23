from urllib.parse import urljoin, quote, unquote

def get_base_host(url):
    return urljoin(url, '/').rstrip('/')

def extract_uuid(url):
    return url.rstrip('/').split('/')[-1]

def percent_encode(url):
    return quote(url, safe='')

def percent_decode(url):
    return unquote(url)