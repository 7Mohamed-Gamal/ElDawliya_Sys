from django.http import HttpResponse

def test_view(request):
    """A simple view to test if the server is working."""
    return HttpResponse("Server is working!")
