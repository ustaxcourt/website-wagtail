from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache


class LocalLoginView(LoginView):
    template_name = "wagtailadmin/local_login.html"
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if not getattr(settings, "ENABLE_LOCAL_LOGIN", False):
            raise Http404()

        resp = super().dispatch(request, *args, **kwargs)
        resp["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        resp["Cache-Control"] = "no-store"
        return resp
