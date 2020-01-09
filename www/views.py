from django.shortcuts import render
from django.http import HttpResponse

from www.models import Poll, Choice,TextPost

# Create your views here.
def index(request):
    post1 = TextPost(title='Using MongoEngine', content='See the tutorial')
    post1.tags = ['mongodb', 'mongoengine']
    post1.save()
    return HttpResponse("Hello, world. You're at the polls index.")
  

def hello(request):
   return render(request, "hello.html", {})