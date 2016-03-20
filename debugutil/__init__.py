"""General debug util methods based on the logger module."""
from datetime import datetime
import logging
import requests

from django.conf import settings

def debug(code, info=None, logger=None, exc_info=None, extra=None, **kwargs):
    """Debug wrappper for the logging module.

    All debug messages are indicated using a log code, as defined in the
    settings.LOG_CODE dict. With that code a default short description is
    registered, which could contain formatting placeholders. Optionally an
    additional long description can be provided to be appended to this. All
    formatting placeholders should be named and can be provided in the keyword
    arguments of this function, provided that they do not collide with any of
    the explicit keyword arguments defined for this function. In case this is
    unavoidable, the keyword argument `extra` can be used to pass a dict
    containing all formatting values instead. If `extra` is a dict, it is
    assumed to contain *all* the formatting values needed for the message.

    In most cases however, any formatting placeholdes can be passed as
    additional keyword arguments. For example, a log code that has the
    following message "Something unexpected happened: %(error)s",
    can be instantiated by:

        try:
            ...
        catch KeyError as e:
            debug(501, error=str(e))

    :param int code: A numerical three-digit code that indicates the message.
    :param str [info]: A long description of the situation.
    :param str [logger]: A logger identifier.
    :param [exc_info]: See Logger.log for info.
    :param dict [extra]: Mapping of parameters to be used instead of **kwargs.
    :param [**kwargs]: Parameters to be used in formatting the error message.
    """

    if logger is None:
        logger = logging.getLogger()
    elif isinstance(logger, str):
        logger = logging.getLogger(logger)

    code = int(code)
    if code < 100 or code >= 600:
        code = 501

    level = (code // 100) * 10 # Turns 543 into 50

    if not logger.isEnabledFor(level):
        return

    desc = None
    extra = extra if isinstance(extra, dict) else kwargs

    if settings.SHOW_LOG_CODE_DESCRIPTION:
        try:
            desc = settings.LOG_CODES.get(code, 'Unknown code') % extra
        except KeyError as exc:
            code = 503
            extra = {'error': str(exc)}
            try:
                desc = settings.LOG_CODES.get(code, 'Unknown code') % extra
            except KeyError:
                desc = str(exc)

    extra['code'] = code

    log_msg = desc or ""

    if info is not None:
        log_msg = "%s\n%s" % (log_msg, info)

    logger.log(level, log_msg, exc_info=exc_info, extra=extra)

def debug_http_package(http_package, label=None, secret_body_values=None,
                       logger=None, **kwargs):
    """Debug a network package under code 101."""
    label = label or 'HTTP Package'
    output_lines = [label+':']
    if isinstance(http_package, requests.Request) or \
        isinstance(http_package, requests.PreparedRequest):
        output_lines.append("%s %s HTTP/1.1" % (
            http_package.method, http_package.path_url))
        headers = sorted(http_package.headers.items(), key=lambda x: x[0])
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
        headers = sorted(http_package.headers.items(), key=lambda x: x[0])
        for header, value in headers:
            output_lines.append("%s: %s" % (header.title(), value))
    else:
        output_lines.append("Unknown http_package: %s" % (http_package,))
    debug(101, logger=logger, info="\n".join(output_lines), **kwargs)
