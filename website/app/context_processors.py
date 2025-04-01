from django.conf import settings


def build_info(request):
    return {"build_sha": settings.GITHUB_SHA[:6]}
