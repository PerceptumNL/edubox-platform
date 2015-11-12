"""
Adaptation on https://github.com/tkaemming/django-subdomains.
"""
from subdomains.middleware import SubdomainMiddleware
from django.conf import settings
from django.utils.cache import patch_vary_headers

import re
import operator

lower = operator.methodcaller('lower')

UNSET = object()

class SubdomainAppRoutingMiddleware(SubdomainMiddleware):
    def process_request(self, request):
        """
        Sets the current request's ``urlconf`` attribute to the urlconf
        associated with the subdomain, if it is listed in
        ``settings.SUBDOMAIN_URLCONFS``.
        """
        super(SubdomainAppRoutingMiddleware, self).process_request(request)

        subdomain = getattr(request, 'subdomain', UNSET)

        if subdomain is not UNSET:
            if subdomain in settings.SUBDOMAIN_ROUTING:
                routing = settings.SUBDOMAIN_ROUTING.get(subdomain)
                if callable(routing):
                    routing(request)
                else:
                    request.urlconf = routing
            else:
                for pattern, routing in settings.SUBDOMAIN_ROUTING.items():
                    match = re.match(pattern, subdomain)
                    if match:
                        if callable(routing):
                            if match.lastgroup is not None:
                                routing(request, **match.groupdict())
                            else:
                                routing(request, *match.groups())
                        else:
                            request.urlconf = routing
                        break

    def process_response(self, request, response):
        """
        Forces the HTTP ``Vary`` header onto requests to avoid having responses
        cached across subdomains.
        """
        if getattr(settings, 'FORCE_VARY_ON_HOST', True):
            patch_vary_headers(response, ('Host',))

        return response
