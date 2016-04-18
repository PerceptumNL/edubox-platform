"""Signal handlers for code submissions"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.dispatch import Signal
from kb.events.models import CompiledEvent

from codelib.dialects.codeorg.parser import CodeOrgDialect
from codelib.dialects.js.parser import JavaScriptDialect
from codelib.dialects.scratch.parser import ScratchDialect

code_parsed = Signal(providing_args=["user", "code", "code_type"])

@receiver(post_save, sender=CompiledEvent)
def handle_code_compilation(sender, instance, **kwargs):
    if instance.code_type == "codeorg-blockly":
        code = CodeOrgDialect(instance.code)
    elif instance.code_type == "javascript":
        code = JavaScriptDialect(instance.code)
    elif instance.code_type == "scratch":
        code = ScratchDialect(instance.code)
    else:
        code = None

    if code:
        code_parsed.send(sender=type(code), code=code, user=instance.user,
                         code_type=instance.code_type)
