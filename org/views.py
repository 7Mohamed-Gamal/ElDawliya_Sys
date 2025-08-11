from django.http import HttpResponse

def index(request):
    return HttpResponse("Org app is wired correctly.")

# Create your views here.
