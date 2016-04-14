import re

def get_app_by_url(url, group=None, apps=None):
    if apps is None:
        if group is None:
            from kb.apps.models import App
            apps = App.objects.all()
        else:
            apps = group.apps.all()

    for app in apps:
        if re.match(app.identical_urls, url):
            break
    else:
        return None
    return app

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

def route_links_in_text(request, text, group, apps=None):
    from kb.helpers import create_token
    rgx = r'(?:https?:\/\/)?(?:[\da-z\.-]+)\.(?:[a-z\.]{2,6})(?:[\/\w\.-]*)*\/?'
    apps = apps or group.apps.all()
    links = re.findall(rgx, text)
    for link in links:
        app = get_app_by_url(link, apps=apps)
        if app is None:
           continue

        token = create_token(
            request.user.pk,
            group.pk,
            app.pk).decode('utf-8')
        text = text.replace(link, "%s?token=%s" % (
            get_routed_url(request, link), token))

    return text
