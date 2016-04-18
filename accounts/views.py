from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from allauth.account.views import PasswordChangeView

from kb.helpers import unpack_token
from kb.apps.models import App

def _get_user_info_dict(user):
    name = user.profile.full_name.strip()
    if not name and user.profile.alias:
        name = user.profile.alias.split('@')[0]
    elif not name:
        name = user.username.split('@')[0]

    from django.utils import timezone
    local_tz = timezone.get_current_timezone()

    return {'name': name,
            'last_login': user.last_login.astimezone(local_tz).strftime(
                "%d %B %H:%M") if user.last_login else '-',
            'isTeacher': user.profile.is_teacher()}

def get_user_info(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    group_id = request.GET.get('group')
    if group_id is not None:
        from kb.groups.models import Group, Membership
        group = get_object_or_404(Group, pk=int(group_id))
        if not request.user.is_superuser:
            try:
                membership = Membership.objects.get(
                    user=request.user.profile, group=group)
            except Membership.DoesNotExist:
                return HttpResponse(status=403);
            else:
                show_group = (membership.role.role == 'Teacher')
        else:
            show_group = True

        if show_group:
            members = Membership.objects.filter(group=group)
            return JsonResponse({'info': {
                member.user.user.pk: _get_user_info_dict(member.user.user) for
                    member in members }})
        else:
            return HttpResponse(status=403);
    else:
        return JsonResponse({
            'info': _get_user_info_dict(request.user) })

def login_user_into_app(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    token = request.GET.get('token', None)
    if token is None:
        return HttpResponse('No token.', status=400)

    unpacked = unpack_token(token)
    if unpacked is None:
        return HttpResponse('Illegal token', status=400)

    if int(unpacked['user']) != request.user.pk:
        return HttpResponse('User does not match.', status=403)

    try:
        app = App.objects.get(pk=unpacked['app'])
    except App.DoesNotExist:
        return HttpResponse('Unknown app.', status=400)

    from connectors import get_app_connector
    connector = get_app_connector(app)
    if connector is None:
        return HttpResponse('Could not find connector.', status=500)

    if connector.is_logged_in(token=token):
        return HttpResponse(status=200)

    credentials = connector.get_or_create_credentials(
        token, request.user, app.pk)
    if credentials is None:
        return HttpResponse('Could not find/create credentials.', status=503)

    if connector.login(token, credentials):
        return HttpResponse(status=200)
    else:
        return HttpResponse('Could not login.', status=500)

class RedirectPasswordChangeView(PasswordChangeView):
    success_url = None
    redirect_field_name = "next"

    def get_success_url(self):
        from allauth.account.utils import get_next_redirect_url
        # Explicitly passed ?next= URL takes precedence
        ret = (get_next_redirect_url(self.request,
                                     self.redirect_field_name)
               or self.success_url)
        return ret

    def get_context_data(self, **kwargs):
        from allauth.utils import get_request_param
        ret = super().get_context_data()
        redirect_field_value = get_request_param(self.request,
                                                 self.redirect_field_name)
        ret['redirect_field_name'] = self.redirect_field_name
        ret['redirect_field_value'] = get_request_param(self.request,
                                                        self.redirect_field_name)
        return ret

redirect_password_change = login_required(RedirectPasswordChangeView.as_view())
