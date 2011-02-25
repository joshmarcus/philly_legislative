# Create your views here.
from django.http import HttpResponse

def index(request):
    return HttpResponse("this is the index")

def create(request):
    return HttpResponse("this is the create page")

def edit(request, subscription_id):
    return HttpResponse("this is the update page for %s" % subscription_idi )

def delete(request):
    return HttpResponse("this is the delete page")

