from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import QueryDict
from kb.events.models import SubmittedEvent
from .models import Activity, ActivityCompletion

@receiver(post_save, sender=SubmittedEvent)
def handle_activity_completion(sender, instance, **kwargs):
    print('handle_activity_completion')
    try:
        activity = Activity.objects.get(url=instance.obj, app=instance.app);
    except Activity.DoesNotExist:
        print('no activity')
        return

    print('activity found')

    try:
        submission = QueryDict(instance.submission)
        print(submission)
        if submission.get('testResult',0) == 100:
            ActivityCompletion.objects.get_or_create(
                activity=activity, user=instance.user)
    except Exception:
        print('submission cannot be parsed')
        return;
