from django.http import HttpResponse

def index(request):
    return HttpResponse("Employees app is wired correctly.")

# Create your views here.
