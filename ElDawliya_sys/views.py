from django.http import HttpResponse

def test_view(request):
    """A simple view to test if the server is working."""
    return HttpResponse("Server is working!")

from django.shortcuts import render

def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)

def custom_403(request, exception):
    return render(request, 'errors/403.html', status=403)
