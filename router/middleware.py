"""
Adaptation of https://github.com/tkaemming/django-subdomains.
"""
from subdomains.middleware import SubdomainMiddleware
from django.conf import settings
from django.utils.cache import patch_vary_headers

import re
import operator

lower = operator.methodcaller('lower')

UNSET = object()

class SubdomainAppRoutingMiddleware(SubdomainMiddleware):
    """
    Middleware to route the request to different views based on the subdomain.
    """

    def process_request(self, request):
        """
        Compares the current request to the entries in the routing dict set in
        ``settings.SUBDOMAIN_ROUTING``. The current request's subdomain is
        matched to the keys of the routing dict. First as an exact match and,
        when that has no match, as a regex pattern match.

        The subdomain is retrieved from the request object, put there by
        :py:meth:`SubdomainMiddleware.process_request`. The subdomain can be
        set to None, which is therefore also a valid key for the routing dict
        denoting the situation when there is not subdomain in the request.

        The router dict's values can be either a string or a callable. When the
        value is a string, it is interpreted as a reference to the urlconf
        module through which the request's url must be matched. This is
        handled by setting ``request.urlconf`` to the matched valued.

        When the value is a callable, it will be called with the request
        object. In case the matching routing dict's key contained regex groups,
        the matched groups will be passed to the router dict's callable in
        addition to the request object. The router dict's regex patterns are
        assumed to have all groups either named or not.  Based on whether the
        resulting :py:meth:`re.MatchObject.lastgroup` was None, the matches
        will be passed to the callable as arguments or keyword arguments.

        :param request: The request to route based on its subdomain.
        :type request: :py:class:`django.http.HttpRequest`
        :return: return of matched callable or None
        :rtype: :py:class:`django.http.HttpResponse` or NoneType
        """
        super(SubdomainAppRoutingMiddleware, self).process_request(request)

        subdomain = getattr(request, 'subdomain', UNSET)

        from router import Router
        routing_table = settings.SUBDOMAIN_ROUTING
        routing_table.update(Router.get_subdomain_routing_mapping())

        if subdomain is not UNSET:
            if subdomain in routing_table:
                routing = routing_table.get(subdomain)
                if callable(routing):
                    return routing(request)
                else:
                    request.urlconf = routing
            else:
                for pattern, routing in routing_table.items():
                    if pattern is None:
                        continue
                    match = re.match(pattern, subdomain)
                    if match:
                        if callable(routing):
                            if match.lastgroup is not None:
                                return routing(request, **match.groupdict())
                            else:
                                return routing(request, *match.groups())
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
