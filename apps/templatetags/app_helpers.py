from django import template
from django.template.loader import get_template
from django.template.defaultfilters import stringfilter
from django.core.urlresolvers import reverse

import uuid
import re

register = template.Library()

def _split_args_and_kwargs(arguments):
    """Split a list of argument strings into args and kwargs"""
    kwargs = {}
    args = []
    for arg in arguments:
        if '=' in arg:
            key, val = arg.split("=")
            kwargs[key] = val
        else:
            args.append(arg)
    return (args, kwargs)

@register.tag('form')
def do_form(parser, token):
    """Block template tag for Ajax-driven forms.
    {% form [path [cb]] %}
      <input ... />
      <input type='submit' ... />
    {% endform %}

    Keyword arguments are also supported, as well as a combination.

    Arguments:
     path   - Location of the script to post to, which will be expanded
              with the expand_location() function. (default: current URL)
     cb     - Name of function that handles the scripts' response
              (default: App.current().render)
    """
    args, kwargs = _split_args_and_kwargs(token.split_contents()[1:])
    nodelist = parser.parse(('endform',))
    parser.delete_first_token()
    return FormNode(nodelist, *args, **kwargs)

class FormNode(template.Node):
    def __init__(self, nodelist, path=None, cb=None):
        self.nodelist = nodelist
        self.submit_path = path or ""
        self.callback_fn = cb or "App.current().render"

    def render(self, context):
        inner_output = self.nodelist.render(context)
        submit_path = expand_location(context['request'], self.submit_path)
        form_id = str(uuid.uuid4())
        return get_template("app_helpers/form.html").render(
                request=context['request'],
                context={
                    "form_id": form_id,
                    "inner_output": inner_output,
                    "submit_path": submit_path,
                    "callback_fn": self.callback_fn
                })

@register.tag('link')
def do_link(parser, token):
    """Block template tag for links.
    {% link href=url attributes %}
      text
    {% endlink %}
    """
    args, kwargs = _split_args_and_kwargs(token.split_contents()[1:])
    nodelist = parser.parse(('endlink',))
    parser.delete_first_token()
    return LinkNode(nodelist, kwargs)

class LinkNode(template.Node):
    def __init__(self, nodelist, attr={}):
        self.nodelist = nodelist
        self.attr = attr

    def render(self, context):
        link_id = str(uuid.uuid4())
        text = self.nodelist.render(context)
        url = expand_location(context['request'], self.attr.pop("href"))
        attr = " ".join([k +"="+ self.attr[k] for k in self.attr.keys()])
        return get_template("app_helpers/link.html").render(
                request=context['request'],
                context={
                    "link_id": link_id,
                    "url": url,
                    "text": text,
                    "attr": attr
                })

def expand_location(request, location):
    """Expand location to fully-qualified URL

     There are four different type of paths that can be handled.
       1) Fully-qualified paths (e.g. http://www.example.com)
       2) Absolute paths (e.g. /full/path/to/script)
       3) Relative paths (e.g. path/to/script)
       4) Service paths (e.g. service:echo or service:echo/path/to/script)

     Fully-qualified paths are kept as-is, but should only be used when the
     script is located at a different domain. In that case it is almost always
     necessary to set the corresponding CORS headers.

     Absolute paths point at a view within this app, with a corresponding URL
     pattern that matches this path from the root of this application's urls.

     Relative paths are similar to absolute paths, but use the location of the
     current request as a base. If the current location ends with a forward
     slash (e.g. /foo/dir/), the relative path is appended. If this is not
     the case (e.g. /foo/file), the relative path is placed after the
     right-most forward slash (i.e. /foo/path/to/script).

     Service paths are a shortcut to the service router path of a specific
     service. Service paths can also contain an additional path that starts at
     the base of the service location (e.g. service:echo/path/to.script).
    """
    # Check if location already contains a protocol
    fqd_match = re.match(r'[a-z:]*//', location)
    if fqd_match:
        # Location is probably located at different server, keep it as-is.
        return location

    # Check if location contains a reference to a service
    service_match = re.search(r'^service:([^/]+)(/.+)?$', location)
    if service_match:
        # Extract service
        service = service_match.group(1)
        path = service_match.group(2) or "/"
        return reverse('service_routing', args=(service, path))

    if hasattr(request, 'outer_resolver_match'):
        app = request.outer_resolver_match.kwargs['app_id']
        if location[:1] == "/":
            return reverse('app_routing', args=(app, location))
        else:
            root = request.outer_resolver_match.kwargs['path']
            if root == "":
                root = "/"
            elif root[-1] != "/":
                root = "/"+"/".join(root.split("/")[:-1])
            return reverse('app_routing', args=(app, root+location))
    else:
        return location if location != "" else "/"
