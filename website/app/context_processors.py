from django.conf import settings


def settings_context(request):
    print("test", settings)
    return {"SETTINGS": settings}
