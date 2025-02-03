from django.shortcuts import render


def redirect_view(request):
    external_url = request.GET.get("url", "/")
    return render(request, "redirect_page.html", {"external_url": external_url})
