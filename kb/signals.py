from django.db.models.signals import post_save
from django.dispatch import receiver

from kb.groups.models import Membership

@receiver(post_save, sender=Membership)
def on_role_change(sender, instance, created, **kwargs):
    if created and instance.role.role != "Teacher":
        return
    else:
        if Membership.objects.filter(user=instance.user,
                                     role__role='Teacher').exists():
            instance.user.is_teacher = True;
            instance.user.save()
        else:
            instance.user.is_teacher = False;
            instance.user.save()
