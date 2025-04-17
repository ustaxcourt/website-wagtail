from django.http import HttpResponse


def explode(request):
    1 / 0  # force a crash
    return HttpResponse("this won't run")
