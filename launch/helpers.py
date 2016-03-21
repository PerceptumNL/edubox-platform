def get_routed_url(request, url, domain=None):
    from urllib.parse import urlsplit, urlunsplit
    from binascii import b2a_hex
    from subdomains.utils import get_domain
    from django.conf import settings

    parts = urlsplit(url)
    domain = parts.netloc or domain
    hashed_domain = "%s.%s" % (
        b2a_hex(bytes(domain, "utf-8")).decode("utf-8"), settings.ROUTER_DOMAIN)

    return urlunsplit((
        settings.ROUTER_PROTOCOL or parts.scheme or request.scheme,
        hashed_domain,
        parts.path,
        parts.query,
        parts.fragment))


def get_routed_app_url(request, app, url='/'):
    from urllib.parse import urlsplit
    return get_routed_url(request, url,
                          domain=urlsplit('http://'+app.root).netloc)
