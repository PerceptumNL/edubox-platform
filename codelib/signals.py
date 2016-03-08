from django.dispatch import Signal

submitted_code_parsed = Signal(providing_args=["user", "code"])
