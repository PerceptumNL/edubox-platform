from django.conf import settings
from datetime import datetime
import requests

def debug(msg, category='DEBUG'):
    """
    Prints a debug message when the setting ``DEBUG`` is set to True.
    Each debug message is preprended with the current time provided by
    :func:`datetime.datetime.now` and the category label."

    :param str msg: The debug message to display
    :param str category: The debug category to display
    """
    if not settings.DEBUG:
        return
    print("[%s] %s - %s" % (datetime.now(), category, msg))

def debug_http_package(http_package, label=None, secret_body_values=None,
        category='DEBUG'):
    if not settings.DEBUG:
        return
    label = label or 'HTTP Package'
    output_lines = [label+':']
    if isinstance(http_package, requests.Request) or \
        isinstance(http_package, requests.PreparedRequest):
        output_lines.append("%s %s HTTP/1.1" % (
            http_package.method, http_package.path_url))
        headers = sorted(http_package.headers.items(), key=lambda x:x[0])
        for header, value in headers:
            output_lines.append("%s: %s" % (header.title(), value))
        if http_package.body is not None:
            output_lines.append("")
            body = http_package.body
            if secret_body_values is not None:
                for secret in secret_body_values:
                    body = body.replace(str(secret), "****")
            output_lines.append(body)
    elif isinstance(http_package, requests.Response):
        output_lines.append("HTTP %s %s" % (
            http_package.status_code, http_package.reason))
        headers = sorted(http_package.headers.items(), key=lambda x:x[0])
        for header, value in headers:
            output_lines.append("%s: %s" % (header.title(), value))
    else:
        output_lines.append("Unknown http_package: %s" % (http_package,))
    debug("\n".join(output_lines), category)
