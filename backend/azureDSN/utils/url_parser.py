from urllib.parse import urljoin

def get_base_host(url):
    return urljoin(url, '/').rstrip('/')

def extract_uuid(url):
    return url.rstrip('/').split('/')[-1]