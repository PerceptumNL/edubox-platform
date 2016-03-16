from django.conf import settings
from datetime import datetime
import requests
import logging

def debug(code, category='DEBUG', logger=None, extra_msg=None, **kwargs):
    """
    Prints a debug message when the setting ``DEBUG`` is set to True.
    Each debug message is preprended with the current time provided by
    :func:`datetime.datetime.now` and the category label."

    :param str msg: The debug message to display
    :param str category: The debug category to display
    """
    if logger is None:
        logger = logging.getLogger()
    elif isinstance(logger, 'str'):
        logger = logging.getLogger(logger)

    desc = settings.LOG_CODES.get(code, 'Unknown code')
    try:
        level = { '1': logging.DEBUG, '2': logging.INFO, '3': logging.WARNING,
                  '4': logging.ERROR, '5': logging.CRITICAL }[code[0]]
    except KeyError:
        level = loggin.ERROR
        code = 'S501'
    if extra_msg is None:
        logger.log(level, "[%s] %s - %s" % (category, code), **kwargs)
    else:
        logger.log(
            level, "[%s] %s - %s\n%s" % (category, code, extra_msg), **kwargs)

def debug_http_package(code, http_package, label=None, secret_body_values=None,
        category='DEBUG', logger=None):
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
    debug(code, category=category, logger=logger, extra_msg="\n".join(output_lines))
