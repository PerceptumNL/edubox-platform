from urllib.parse import urlparse
from django.contrib.sites.models import Site
from django.utils.http import is_safe_url
from allauth.account.adapter import DefaultAccountAdapter

class EduraamAccountAdapter(DefaultAccountAdapter):

    def is_safe_url(self, url):
        if url is None:
            return False
        current_domain = Site.objects.get_current().domain
        url_domain = urlparse(url).netloc
        # Check if the url domain is a subdomain of the current domain
        if url_domain.endswith("."+current_domain):
            return is_safe_url(url=url, host=url_domain)
        return is_safe_url(url=url)
