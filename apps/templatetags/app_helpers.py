from django import template
from django.template.defaulttags import CsrfTokenNode

import uuid

TEMPLATE_FORM = """
<form id="%s">%s%s</form>
<script>
    $(function(){
        $("#%s").submit(function(e){
            data = $(this).serialize()
            $.post("%s", data, %s);
            e.preventDefault();
        });
    });
</script>"""

register = template.Library()

@register.tag('form')
def do_form(parser, token):
    args = token.split_contents()
    if len(args) == 3:
        _, submit_path, callback_fn = args
    elif len(args) == 2:
        _, submit_path = args
        callback_fn = None
    else:
        callback_fn = None
        submit_path = None
    nodelist = parser.parse(('endform',))
    parser.delete_first_token()
    return FormNode(nodelist, submit_path, callback_fn)

class FormNode(template.Node):
    def __init__(self, nodelist, submit_path=None, callback_fn=None):
        self.nodelist = nodelist
        self.submit_path = submit_path or ""
        self.callback_fn = callback_fn or "App.current().render"

    def render(self, context):
        output = self.nodelist.render(context)
        formid = str(uuid.uuid4())
        csrf_token = CsrfTokenNode().render(context)
        return TEMPLATE_FORM % (formid, csrf_token, output, formid,
                self.submit_path, self.callback_fn)
