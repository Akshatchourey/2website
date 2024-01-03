from django.shortcuts import render, redirect
from django.http import HttpResponse
from math import ceil as c
from .models import *

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
    no_of_videos = 12
    page = request.GET.get('page')
    if page is None:
        page = 1
    else:
        page = int(page)
    videos = Video.objects.all()
    length = len(videos)
    videos = videos[(page-1)*no_of_videos: page*no_of_videos]
    if page>1:
        prev=page-1
    else:
        prev = None
    if page < c(length/no_of_videos):
        nxt = page + 1
    else:
        nxt = None
    context = {'videos': videos, 'prev': prev, 'nxt': nxt}
    return render(request, "opcoder/videos.html", context)

def private(request):
    return render(request, "opcoder/private.html")
def photos(request):
    return render(request, "opcoder/photos.html")

def blog(request):
    no_of_posts = 6
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
