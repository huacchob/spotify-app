from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


# Home view (optional, links to major sections)
def home(request: HttpRequest) -> HttpResponse:
    """
    Home view.

    Args:
        request (HttpRequest): Request object passed from urls module.

    Returns:
        HttpResponse: Response object with home page template.
    """
    return render(
        request=request,
        template_name="spotify_integration/home.html",
    )
