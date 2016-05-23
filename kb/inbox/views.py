from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

def message_list(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    message_list = [];

    from django.utils import timezone
    local_tz = timezone.get_current_timezone()
    from .models import Message
    unread_messages = Message.objects.order_by('-pk').filter(
        user=request.user.profile, read=False)
    for message in unread_messages:
        message_list.append({
            'id': message.pk,
            'title': message.title,
            'date': message.datetime.astimezone(local_tz).strftime(
                "%d %B"),
            'summary': message.body})

    return JsonResponse({'messages': message_list})
