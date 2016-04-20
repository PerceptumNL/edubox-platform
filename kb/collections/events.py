from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import QueryDict
from kb.events.models import SubmittedEvent
from .models import Activity, ActivityCompletion

@receiver(post_save, sender=SubmittedEvent)
def handle_activity_completion(sender, instance, **kwargs):
    from re import sub
    try:
        activity = Activity.objects.get(
            url__endswith=sub(r"https?", "", instance.obj),
            app=instance.app);
    except Activity.DoesNotExist:
        return

    try:
        submission = QueryDict(instance.submission)
        if submission.get('pass', 'false') == 'true':
            score = int(submission.get('testResult',0))
            ActivityCompletion.objects.get_or_create(
                activity=activity, score=score, user=instance.user.profile)
    except Exception:
        return;
