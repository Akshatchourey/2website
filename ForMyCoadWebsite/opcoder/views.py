from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, "opcoder/index.html")

def login(request):
    return render(request, "opcoder/login.html")
def sign_up(request):
    return render(request, "opcoder/sign up.html")
def video(request):
    return render(request, "opcoder/video.html")
def private(request):
    return render(request, "opcoder/private.html")
def video_playing(request):
    return render(request, "opcoder/video_playing.html")
def blogs(request):
    return render(request, "opcoder/blogs.html")
def photos(request):
    return render(request, "opcoder/photos.html")
