from django.http import HttpResponse
from django.shortcuts import render

def test_view(request):
    """A simple view to test if the server is working."""
    return HttpResponse("Server is working!")

def ui_demo_view(request):
    """UI Components Demo - Design System Showcase"""
    return render(request, 'ui_demo.html', {
        'show_sidebar': False,
        'show_navbar': True,
        'show_footer': True,
    })

def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)

def custom_403(request, exception):
    return render(request, 'errors/403.html', status=403)
