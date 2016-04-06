"""Signal handlers for code submissions"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.dispatch import Signal
from kb.events.models import CompiledEvent

code_parsed = Signal(providing_args=["user", "code", "code_type"])

@receiver(post_save, sender=CompiledEvent)
def handle_code_compilation(sender, instance, **kwargs):
    if instance.code_type == "codeorg-blockly":
        from connectors.codeorg.parser import codeorg_parse
        code = codeorg_parse(instance.code)
    elif instance.code_type == "javascript":
        from codelib.dialects.js import Dialect
        code = Dialect(instance.code)
    else:
        code = None

    if code:
        code_parsed.send(sender=type(code), code=code, user=instance.user,
                         code_type=instance.code_type)
