from django.shortcuts import render, redirect
from django.http import HttpResponse
from math import ceil as c
from .models import Blog

# Create your views here.


def index(request):
    return render(request, "opcoder/index.html")

def search(request):
    a = (request.GET.get("slug"))
    longblogs = Blog.objects.filter(slug=a).first()
    print(longblogs)
    longblogslist = {'name': longblogs}
    return render(request, 'opcoder/blogpost.html', longblogslist)

def login(request):
    return render(request, "opcoder/login.html")
def sign_up(request):
    return render(request, "opcoder/sign up.html")
def video(request):
    return render(request, "opcoder/videos.html")
def private(request):
    return render(request, "opcoder/private.html")
def video_playing(request):
    return render(request, "opcoder/video_playing.html")
def photos(request):
    return render(request, "opcoder/photos.html")

def blog(request):
    no_of_posts = 3
    page = request.GET.get('page')
    if page is None:
        page = 1
    else:
        page = int(page)
    blogs = Blog.objects.all()
    length = len(blogs)
    blogs = blogs[(page-1)*no_of_posts: page*no_of_posts]
    if page>1:
        prev=page-1
    else:
        prev = None
    if page < c(length/no_of_posts):
        nxt = page + 1
    else:
        nxt = None
    context = {'blogs': blogs, 'prev': prev, 'nxt': nxt}
    return render(request, 'opcoder/blogs.html', context)

def blogpost(request, slug):
    longblogs = Blog.objects.filter(slug=slug).first()
    longblogslist = {'name': longblogs}
    return render(request, 'opcoder/blogpost.html', longblogslist)
