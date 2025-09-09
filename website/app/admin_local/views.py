from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import Http404


class LocalLoginView(LoginView):
    template_name = "wagtailadmin/local_login.html"
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if not getattr(settings, "ENABLE_LOCAL_LOGIN", False):
            raise Http404()
        configured_tokens = {
            t
            for t in [
                getattr(settings, "LOCAL_LOGIN_TOKEN", ""),
                getattr(settings, "CYPRESS_LOCAL_LOGIN_TOKEN", ""),
            ]
            if t
        }
        token = request.GET.get("token", "")
        if configured_tokens and token not in configured_tokens:
            raise Http404()
        resp = super().dispatch(request, *args, **kwargs)
        resp["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return resp
