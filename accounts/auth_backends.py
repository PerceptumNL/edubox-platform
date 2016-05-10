from allauth.account.auth_backends import AuthenticationBackend, app_settings

class ExtendedAuthenticationBackend(AuthenticationBackend):

    def authenticate(self, **credentials):
        ret = super().authenticate(**credentials)
        if ret is None:
            ret = self._authenticate_by_alias(**credentials)
        return ret

    def _authenticate_by_alias(self, **credentials):
        from kb.models import UserProfile

        alias = credentials.get('email', credentials.get('username'))
        if alias:
            for profile in UserProfile.objects.filter(alias__iexact=alias):
                if profile.user.check_password(credentials["password"]):
                    return profile.user
        return None
