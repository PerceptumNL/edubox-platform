from django.dispatch import Signal

parsed_submission = Signal(providing_args=["user", "code"])
